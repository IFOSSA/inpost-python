from typing import Any


# ------------------ Base ------------------- #
class BaseInpostError(Exception):
    """Base exception to inherit from

    :param reason: reason of BaseInpostError happening
    :type reason: typing.Any"""

    def __init__(self, reason):
        """Constructor method

        :param reason: Reason of error
        :type reason: Any
        """
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self) -> Any:
        """Gets stacktrace of raised exception
        :return: reason why exception occured
        :rtype: Any"""
        return self.reason


# ----------------- Parcels ----------------- #


class ParcelTypeError(BaseInpostError):
    """Is raised when expected :class:`ParcelType` does not match with actual one"""

    pass


class NoParcelError(BaseInpostError):
    """Is raised when no parcel is set in :class:`Parcel`"""

    pass


class UnknownStatusError(BaseInpostError):
    """Is raised when no status matches"""

    pass


class UnidentifiedParcelError(BaseInpostError):
    """Is raised when no other :class:`Parcel` error match"""

    pass


# ----------------- API ----------------- #
class NotAuthenticatedError(BaseInpostError):
    """Is raised when `Inpost.auth_token` is missing"""

    pass


class ReAuthenticationError(BaseInpostError):
    """Is raised when `Inpost.auth_token` has expired"""

    pass


class PhoneNumberError(BaseInpostError):
    """Is raised when `Inpost.phone_number` is invalid or unexpected error connected with phone number occurs"""

    pass


class SmsCodeError(BaseInpostError):
    """Is raised when `Inpost.sms_code` is invalid or unexpected sms_code occurs"""

    pass


class RefreshTokenError(BaseInpostError):
    """Is raised when `Inpost.refr_token` is invalid or unexpected error connected with refresh token occurs"""

    pass


class NotFoundError(BaseInpostError):
    """Is raised when method from :class:`Inpost` returns 404 Not Found HTTP status code"""

    pass


class UnauthorizedError(BaseInpostError):
    """Is raised when method from :class:`Inpost` returns 401 Unauthorized HTTP status code"""

    pass


class UnidentifiedAPIError(BaseInpostError):
    """Is raised when no other API error match"""

    pass


# ----------------- Other ----------------- #
class UserLocationError(BaseInpostError):
    pass


class SingleParamError(BaseInpostError):
    """Is raised when only one param must be filled in but got more"""

    pass


class MissingParamsError(BaseInpostError):
    """Is raised when none of params are filled"""

    pass


class UnidentifiedError(BaseInpostError):
    """Is raised when no other error match"""

    pass
