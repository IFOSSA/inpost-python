# ----------------- Parcels ----------------- #
from typing import Any


class UnidentifiedParcelError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self):
        return self.reason


class ParcelTypeError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self):
        return self.reason


# ----------------- API ----------------- #
class NotAuthenticatedError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self):
        return self.reason


class ReAuthenticationError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self):
        return self.reason


class PhoneNumberError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self):
        return self.reason


class SmsCodeConfirmationError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self):
        return self.reason


class RefreshTokenException(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self):
        return self.reason


class UnidentifiedAPIError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self):
        return self.reason


# ----------------- Other ----------------- #
class UserLocationError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self):
        return self.reason


class UnidentifiedError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason: Any = reason

    @property
    def stacktrace(self):
        return self.reason
