# ----------------- Parcels ----------------- #
from typing import Optional, Any


class SomeParcelError(Exception):
    pass


# ----------------- API ----------------- #
class NotAuthenticatedError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.msg: str = Optional[str]
        self.reason: Any = Optional[Any]

    @property
    def stack(self):
        return self.reason


class ReAuthenticationError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.msg: str = Optional[str]
        self.reason: Any = Optional[Any]

    @property
    def stack(self):
        return self.reason


class PhoneNumberError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.msg: str = Optional[str]
        self.reason: Any = Optional[Any]

    @property
    def stack(self):
        return self.reason


class SmsCodeConfirmationError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.msg: str = Optional[str]
        self.reason: Any = Optional[Any]

    @property
    def stack(self):
        return self.reason


class SomeAPIError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.msg: str = Optional[str]
        self.reason: Any = Optional[Any]

    @property
    def stack(self):
        return self.reason


# ----------------- Other ----------------- #
class NotImplementedError(Exception):
    pass
