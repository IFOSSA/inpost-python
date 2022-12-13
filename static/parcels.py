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

    def __eq__(self, other):
        ...


class ParcelCarrierSize(ParcelBase):
    A = 1
    B = 2
    C = 3
    D = 4


class ParcelLockerSize(ParcelBase):
    A = 1
    B = 2
    C = 3


class ParcelDeliveryType(ParcelBase):
    PARCELLOCKER = 1
    CARRIER = 2


class ParcelShipmentType(ParcelBase):
    PARCELLOCKER = 1
    CARRIER = 2
    PARCELPOINT = 3


class ParcelAdditionalInsurance(ParcelBase):
    UNINSURANCED = 1
    ONE = 2  # UPTO 5000
    TWO = 3  # UPTO 10000
    THREE = 4  # UPTO 20000


class ParcelForm(ParcelBase):
    OUTGOING = 1
    INCOMING = 2


class ParcelStatus(ParcelBase):
    CREATED = 1
    CUSTOMERSTORED = 2
    CUSTOMERSENT = 3
    SENT = 4
    INTRANSIT = 5
    RETURNEDTOSORTINGCENTER = 6
    DELIVEREDTOSORTINGCENTER = 7
    RETURNEDTOSENDER = 8
    PREPARED = 9
    CUSTOMERDELIVERING = 10
    STORED = 11
    EXPIRED = 12
    AVIZO = 13
    RETURNEDTOAGENCY = 14
    RETUNEDTOAGENCY = 15
    DELIVEREDTOAGENCY = 16
    CANCELLED = 17
    LABELEXPIRED = 18
    LABELDESTROYED = 19
    MISSING = 20
    CLAIMED = 21
    NOTDELIVERED = 22
    OVERSIZED = 23
    DELIVERED = 24


class ParcelServiceName(ParcelBase):
    ALLEGRO_PARCEL = 1
    ALLEGRO_PARCEL_SMART = 2
    ALLEGRO_LETTER = 3
    ALLEGRO_COURIER = 4
    STANDARD = 5
    STANDARD_PARCEL_SMART = 6
    PASS_THRU = 7
    CUSTOMER_SERVICE_POINT = 8
    REVERSE = 9
    STANDARD_COURIER = 10
    REVERSE_RETURN = 11
