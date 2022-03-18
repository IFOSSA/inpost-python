from enum import Enum


class ParcelBase(Enum):
    def __gt__(self, other):
        ...

    def __ge__(self, other):
        ...

    def __le__(self, other):
        ...

    def __lt__(self, other):
        ...


class ParcelDelivery(ParcelBase):
    A = 1
    B = 2
    C = 3
    D = 4


class ParcelLocker(ParcelBase):
    A = 1
    B = 2
    C = 3
