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
        if isinstance(other, ParcelBase):
            return self.name == other.name

        return False


class ParcelCarrierSize(ParcelBase):
    A = '8x38x64'
    B = '19x38x64'
    C = '41x38x64'
    D = '50x50x80'
    OTHER = 'UNKNOWN'


class ParcelLockerSize(ParcelBase):
    A = '8x38x64'
    B = '19x38x64'
    C = '41x38x64'


class ParcelDeliveryType(ParcelBase):
    parcel_locker = 'Paczkomat'
    courier = 'Kurier'
    parcel_point = 'PaczkoPunkt'


class ParcelShipmentType(ParcelBase):
    parcel = 'Paczkomat'
    courier = 'Kurier'
    parcel_point = 'PaczkoPunkt'


class ParcelAdditionalInsurance(ParcelBase):
    UNINSURANCED = 1
    ONE = 2  # UPTO 5000
    TWO = 3  # UPTO 10000
    THREE = 4  # UPTO 20000


class ParcelType(ParcelBase):
    TRACKED = 'Przychodzące'
    SENT = 'Wysłane'
    RETURNS = 'Zwroty'


class ParcelStatus(ParcelBase):
    CONFIRMED = 'Potwierdzona'
    COLLECTED_FROM_SENDER = 'Odebrana od nadawcy'
    DISPATCHED_BY_SENDER_TO_POK = 'Nadana w PaczkoPunkcie'
    DISPATCHED_BY_SENDER = 'Nadana w paczkomacie'
    TAKEN_BY_COURIER = 'Odebrana przez Kuriera'
    TAKEN_BY_COURIER_FROM_POK = 'Odebrana z PaczkoPunktu nadawczego'
    ADOPTED_AT_SOURCE_BRANCH = 'Przyjęta w oddziale'
    ADOPTED_AT_SORTING_CENTER = 'Przyjęta w sortowni'
    SENT_FROM_SOURCE_BRANCH = 'Wysłana z oddziału'
    OUT_FOR_DELIVERY = 'Wydana do doręczenia'
    OUT_FOR_DELIVERY_TO_ADDRESS = 'Gotowa do doręczenia'
    READY_TO_PICKUP = 'Gotowa do odbioru'
    DELIVERED = 'Doręczona'


class ParcelOwnership(ParcelBase):
    FRIEND = 'Zaprzyjaźniona'
    OWN = 'Własna'


# both are the same, only for being clear
class CompartmentExpectedStatus(ParcelBase):
    OPENED = 'Otwarta'
    CLOSED = 'Zamknięta'


class CompartmentActualStatus(ParcelBase):
    OPENED = 'Otwarta'
    CLOSED = 'Zamknięta'


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
