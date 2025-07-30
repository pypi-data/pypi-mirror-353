import json
import webbrowser
from collections.abc import Callable
from typing_extensions import Any

from oauthlib.oauth2.rfc6749.errors import InsecureTransportError, raise_from_error
from oauthlib.oauth2.rfc6749.utils import is_secure_transport, list_to_scope
from oauthlib.oauth2.rfc8628.clients import DeviceClient
from requests import Response
from requests.sessions import merge_setting
from requests.structures import CaseInsensitiveDict
from requests_oauthlib import OAuth2Session
from tenacity import Retrying, retry_if_exception_type, stop_after_delay, wait_fixed

from . import exception


class DeviceAuthorizationGrantSession(OAuth2Session):
    """
    An OAuth2 session that implements the Device Authorization Grant flow as defined in RFC 8628. Use the `authorize`
    method to initiate the flow, which will prompt the user to authorize the device. The session will poll the
    Authorization Server until the user has authorized the device, until the device code expires, or the request is
    otherwise declined by the user or the Authorization Server.

    See: https://datatracker.ietf.org/doc/html/rfc8628
    """

    DEFAULT_DEVICE_CODE_INTERVAL_SECONDS = 5

    def __init__(
        self,
        client_id: str,
        client: DeviceClient | None = None,
        auto_refresh_url: str | None = None,
        auto_refresh_kwargs: dict[str, Any] | None = None,
        scope: list[str] | None = None,
        device_code_interval: int | None = None,
        token: dict[str, Any] | None = None,
        token_updater: Callable[[dict[str, Any]], None] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs,
    ):
        """Construct a new OAuth2 DeviceAuthorizationGrant client session.

        :param client_id: Client id obtained during registration
        :param client: A :class:`oauthlib.oauth2.DeviceClient` to be used. A
                      new instance is created if not provided.
        :param scope: List of scopes you wish to request access to.
        :param token: Token dictionary, must include access_token
                      and token_type.
        :param device_code_interval: The interval in seconds the client should wait
                      between polling the token endpoint. Defaults to 5 seconds.
        :param auto_refresh_url: Refresh token endpoint URL, must be HTTPS. Supply
                           this if you wish the client to automatically refresh
                           your access tokens.
        :param auto_refresh_kwargs: Extra arguments to pass to the refresh token
                      endpoint.
        :param token_updater: Method with one argument, token, to be used to update
                        your token database on automatic token refresh. If not
                        set a TokenUpdated warning will be raised when a token
                        has been refreshed. This warning will carry the token
                        in its token argument.
        :param headers: Default headers to include on all requests. Defaults to None.
        :param kwargs: Arguments to pass to the Session constructor.
        """

        # Refresh always requires the client_id
        required_refresh_kwargs = {"client_id": client_id, "include_client_id": True}
        auto_refresh_kwargs = merge_setting(
            required_refresh_kwargs, auto_refresh_kwargs, dict_class=CaseInsensitiveDict
        )

        if client is not None:
            if not isinstance(client, DeviceClient):
                raise ValueError("client must be an instance of oauthlib.oauth2.DeviceClient")
        else:
            client = DeviceClient(client_id, scope=scope, **kwargs)  # type: ignore

        # NOTE: This isn't actually required by code, just by some language servers to identify it exists
        self._client = client

        super().__init__(
            client_id=client_id,
            client=client,
            scope=scope,
            token=token,
            auto_refresh_url=auto_refresh_url,
            auto_refresh_kwargs=auto_refresh_kwargs,
            token_updater=token_updater,
            **kwargs,
        )

        self.headers = merge_setting(headers, self.headers, dict_class=CaseInsensitiveDict)

        self.device_code: str | None = None
        self.device_code_interval = device_code_interval or self.DEFAULT_DEVICE_CODE_INTERVAL_SECONDS

        # This hook is needed to validate possible Device Access Token Responses, as they are not currently
        # handled by oauthlib.
        self.register_compliance_hook("access_token_response", self.validate_device_access_token_response)

    def authorization_url(self, url: str, **kwargs) -> tuple[str, str]:
        """Gets a Device Authorization URL by initiating a Device Authorization Request.
        Returned `state` is the User Code from the Device Authorization Response.
        See `Section 3.1`_.

        :param url: Device Authorization Endpoint url, must be HTTPS.
        :param kwargs: Extra parameters to include.
        :return: A tuple of the Device Authorization URL and the User Code.

        .. _`Section 3.1`: https://datatracker.ietf.org/doc/html/rfc8628#section-3.1
        """

        if not is_secure_transport(url):
            raise InsecureTransportError()

        params = self.prepare_device_authorization_request_params(**kwargs)

        response = self.post(url=url, data=params)
        return self.parse_device_authorization_request_body_response(response.text)

    def prepare_device_authorization_request_params(self, scope=None, **kwargs) -> dict[str, Any]:
        """Prepare a device authorization request as per `Section 3.1`_.

        :param scope: List of scopes to request. Must be equal to
            or a subset of the scopes granted when obtaining the refresh
            token. If none is provided, the ones provided in the constructor are
            used.
        :param kwargs: Additional parameters to included in the request.
        :returns: The prepared request parameters.

        .. _`Section 3.1`: https://datatracker.ietf.org/doc/html/rfc8628#section-3.1
        """

        params = {"client_id": self.client_id}

        if scope:
            params["scope"] = list_to_scope(scope)
        else:
            params["scope"] = list_to_scope(self.scope)

        for k in kwargs:
            if kwargs[k]:
                params[str(k)] = kwargs[k]

        return params

    def parse_device_authorization_request_body_response(self, body: str) -> tuple[str, str]:
        """Parse the JSON response body for a device authorization request.

        The authorization server issues a device authorization response as described in
        `Section 3.2`_.

        :param body: The response body from the token request.
        :return: A tuple of the verification URI and the user code (state).
        :raises: :py:class:`oauthlib.oauth2.errors.OAuth2Error` if response is invalid.

        A successful response should always contain:

        **device_code**
            The device code issued by the authorization server. Often
            a random string.

        **user_code**
            The end-user verification code.

        **verification_uri**
            The end-user verification URI on the authorization server.
            The URI should be short and easy to remember as end users
            will be asked to manually type it into their user agent.

        **expires_in**
            The lifetime in seconds of the "device_code" and
            "user_code".

        While it is not mandated it is recommended that the provider include:

        **interval**
            The minimum amount of time in seconds that the client
            SHOULD wait between polling requests to the token endpoint. If no
            value is provided, clients MUST use 5 as the default.

         **verification_uri_complete**
            A verification URI that includes the "user_code" (or
            other information with the same function as the "user_code"),
            which is designed for non-textual transmission.

        .. _`Section 3.2`: https://datatracker.ietf.org/doc/html/rfc8628#section-3.2
        """

        params = json.loads(body)

        self.validate_device_authorization_parameters(params)

        # TODO: We might not be able to rely on the complete url; this will probably require a bit of a rethink of how
        # we reuse the authorization_url method override.
        if "verification_uri_complete" in params:
            # If the auth server provides a complete URL, use that
            user_url = params["verification_uri_complete"]
        else:
            user_url = params["verification_uri"]

        # HACK: Borrow the state parameter to store the User Code
        state = params["user_code"]

        self.device_code = params["device_code"]
        self.device_code_expires_in = params["expires_in"]

        if "interval" in params:
            self.device_code_interval = params["interval"]

        return user_url, state

    def validate_device_authorization_parameters(self, params: dict[str, str | int]) -> None:
        if "error" in params:
            raise_from_error(params["error"], params)  # type: ignore

        if "device_code" not in params:
            raise exception.MissingDeviceCodeError(description="Missing device code parameter.")

        if "user_code" not in params:
            raise exception.MissingUserCodeError(description="Missing user code parameter.")

        if "verification_uri" not in params:
            raise exception.MissingVerificationUriError(description="Missing verification URI parameter.")

        if "expires_in" not in params:
            raise exception.MissingExpiresInError(description="Missing expires in parameter.")

    def start_flow(
        self,
        device_auth_url: str,
        token_url: str,
        try_open_browser: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Initiate the Device Authorization Grant flow; this will prompt the user to authorize the device and block
        the thread until a response is received or a timeout occurs.

        :param device_auth_url: Device Authorization Endpoint url, must be HTTPS.
        :param token_url: The token endpoint, must be HTTPS.
        :param try_open_browser: If True, the session will attempt to open the
                                 authorization URL in a web browser. Defaults to False.
        :param kwargs: Extra parameters to include in the authorization and token requests.
        :return: An access token dict
        """

        authorization_url, user_code = self.authorization_url(device_auth_url, **kwargs)

        self.authorize(
            authorization_url=authorization_url,
            user_code=user_code,
            try_open_browser=try_open_browser,
        )

        return self.wait_for_authorization(token_url, **kwargs)

    def authorize(
        self,
        authorization_url: str,
        user_code: str,
        try_open_browser: bool = False,
    ) -> None:
        """
        Begins the Device Authorization process by prompting the user to authorize the device via the provided
        URL and the User Code - these can be obtained via the `authorization_url` method.
        If `try_open_browser` is True, it will attempt to open the authorization URL in a web browser.

        :param authorization_url: User Device Authorization url, must be HTTPS.
        :param user_code: The User Code that the user will be expected to enter to authorize the device.
        :param try_open_browser: If True, the session will attempt to open the
                                 authorization URL in a web browser. Defaults to False.
        """

        if not is_secure_transport(authorization_url):
            raise InsecureTransportError()

        # NOTE: Always display the message even if try_open_browser is False
        # See: https://datatracker.ietf.org/doc/html/rfc8628#section-3.3.1
        print(
            "Device authorization required; "
            f"open the following URL in a browser and enter the code {user_code} to proceed: {authorization_url}"
        )

        if try_open_browser:
            try:

                print("Attempting to open the authorization URL in a web browser...")
                webbrowser.open(authorization_url, new=2, autoraise=True)

            except Exception as e:
                print(f"Failed to open browser: {e}")

    def check_authorization(self, token_url: str, **kwargs) -> bool:
        """
        Returns True if the token URL returns a valid access token for the device code, indicating that the device has
        been authorized by the user. If the device code is still pending authorization, it will return False, or will
        raise an exception if the Authorization Server indicates that the client should slow down polling, the user has
        declined the request, or the device code has expired.

        :param token_url: The token endpoint, must be HTTPS.
        :param kwargs: Extra parameters to include in the fetch token requests.
        :raises: :py:class:`requests_oauthlib_dags.exception.SlowDownError` if the Authorization Server indicates that
            the client should slow down polling. See: https://datatracker.ietf.org/doc/html/rfc8628#section-3.5
        :raises: :py:class:`requests_oauthlib_dags.exception.AccessDeniedError` if the user has declined the request.
        :raises: :py:class:`requests_oauthlib_dags.exception.ExpiredDeviceCodeError` if the Authorization Server
            reports that the device code has expired.
        :return: True if the device has been authorized, False otherwise.
        """

        try:
            self.fetch_token(token_url, device_code=self.device_code, **kwargs)
            return True

        except exception.AuthorizationPendingError as err:
            if type(err) is exception.SlowDownError:
                raise

        return False

    def wait_for_authorization(self, token_url: str, **kwargs) -> dict[str, Any]:
        """
        When called, blocks the current thread and checks the provided token URL at regular intervals until the user
        has authorized the device, the device code expires, or the request is otherwise declined by the user or the
        Authorization Server.

        :param token_url: The token endpoint, must be HTTPS.
        :param kwargs: Extra parameters to include in the fetch token requests.
        :return: An access token dict
        """

        # Keep attempting to fetch the auth token until the user has authorized the device.
        # Uses the parameters from the Authorization Server to determine how long to retry, and how often.
        for attempt in Retrying(
            retry=retry_if_exception_type(exception.AuthorizationPendingError),
            stop=stop_after_delay(self.device_code_expires_in),
            wait=wait_fixed(self.device_code_interval),
            retry_error_cls=exception.DeviceAuthorizationTimeoutError,
        ):
            with attempt:
                try:
                    return self.fetch_token(token_url, device_code=self.device_code, **kwargs)

                except exception.SlowDownError:
                    # Authorization Server indicated that we should slow down polling by at least another
                    # 5 seconds, but exponential backoff is recommended, so that's what we'll do.
                    # See: https://datatracker.ietf.org/doc/html/rfc8628#section-3.5
                    attempt.retry_state.retry_object.wait.wait_fixed *= 2  # type: ignore
                    raise

        # NOTE: This should never get hit but is here for the benefit of language servers
        return self.token

    def validate_device_access_token_response(self, response: Response) -> Response:
        params = json.loads(response.text)
        if "error" in params:
            error = params["error"]
            self.raise_from_error(error, params)
            # Fallback to RFC6749 error handling
            raise_from_error(error, params)

        return response

    def raise_from_error(self, error: str | int, params: dict) -> None:
        kwargs = {
            "description": params.get("error_description"),
            "uri": params.get("error_uri"),
            "state": params.get("state"),
        }
        for cls in exception.RFC8628_Errors:
            if cls.error == error:
                raise cls(**kwargs)
