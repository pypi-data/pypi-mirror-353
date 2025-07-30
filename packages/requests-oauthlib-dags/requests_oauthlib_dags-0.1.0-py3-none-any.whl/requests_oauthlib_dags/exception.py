from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from requests import Timeout
from tenacity import RetryError


class DeviceAuthorizationTimeoutError(Timeout, RetryError):
    """The user did not respond to the device authorization prompt in time."""


class MissingDeviceCodeError(OAuth2Error):
    error = "missing_device_code"


class MissingUserCodeError(OAuth2Error):
    error = "missing_user_code"


class MissingVerificationUriError(OAuth2Error):
    error = "missing_verification_uri"


class MissingVerificationUriCompleteError(OAuth2Error):
    error = "missing_verification_uri_complete"


class MissingExpiresInError(OAuth2Error):
    error = "missing_expires_in"


# TODO: Replace the following errors with imports from oauthlib.oauth2.rfc8628.errors when released
class AuthorizationPendingError(OAuth2Error):
    """
    The authorization request is still pending as the end user hasn't yet completed the user interaction steps.
    """

    error = "authorization_pending"


class SlowDownError(AuthorizationPendingError):
    """
    The authorization request is still pending and polling should continue, but the interval MUST be increased by 5
    seconds for this and all subsequent requests.
    """

    error = "slow_down"


class ExpiredDeviceCodeError(OAuth2Error):
    """
    The device_code has expired and the device authorization session has concluded. The client MAY commence a new
    Device Authorization Request but SHOULD wait for user interaction before restarting to avoid unnecessary polling.
    """

    error = "expired_token"


RFC8628_Errors = [AuthorizationPendingError, SlowDownError, ExpiredDeviceCodeError]
