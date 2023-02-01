from enum import Enum, EnumMeta
from typing import List


class Meta(EnumMeta):  # temporary handler for unexpected keys in enums
    def __getitem__(cls, item):
        try:
            return super().__getitem__(item)
        except KeyError as error:
            return cls.UNKNOWN

    def __getattribute__(cls, item):
        try:
            return super().__getattribute__(item)
        except KeyError as error:
            return cls.UNKNOWN

    def get_all(cls):
        return [getattr(cls, name) for name in cls.__members__]

    def get_without(cls, without: 'ParcelBase' | List['ParcelBase']):
        if isinstance(without, ParcelBase):
            without = [without]

        return [element for element in cls.get_all() if element not in without]


class ParcelBase(Enum, metaclass=Meta):
    """Base :class:`Enum` class to derive from"""

    def __gt__(self, other):
        if isinstance(other, ParcelBase):
            ...

        return False

    def __ge__(self, other):
        if isinstance(other, ParcelBase):
            ...

        return False

    def __le__(self, other):
        if isinstance(other, ParcelBase):
            ...

        return False

    def __lt__(self, other):
        if isinstance(other, ParcelBase):
            ...

        return False

    def __eq__(self, other):
        if isinstance(other, ParcelBase):
            return self.name == other.name

        return False

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items())
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")


class ParcelCarrierSize(ParcelBase):
    """:class:`Enum` that holds parcel size for carrier shipment type"""
    UNKNOWN = 'UNKNOWN DATA'
    A = '8x38x64'
    B = '19x38x64'
    C = '41x38x64'
    D = '50x50x80'
    OTHER = 'UNKNOWN DIMENSIONS'


class ParcelLockerSize(ParcelBase):
    """:class:`Enum` that holds parcel size for parcel locker shipment type"""
    UNKNOWN = 'UNKNOWN DATA'
    A = '8x38x64'
    B = '19x38x64'
    C = '41x38x64'


class ParcelDeliveryType(ParcelBase):
    """:class:`Enum` that holds parcel delivery types"""
    UNKNOWN = 'UNKNOWN DATA'
    parcel_locker = 'Paczkomat'
    courier = 'Kurier'
    parcel_point = 'PaczkoPunkt'


class ParcelShipmentType(ParcelBase):
    """:class:`Enum` that holds parcel shipment types"""
    UNKNOWN = 'UNKNOWN DATA'
    parcel = 'Paczkomat'
    courier = 'Kurier'
    parcel_point = 'PaczkoPunkt'


class ParcelAdditionalInsurance(ParcelBase):
    UNKNOWN = 'UNKNOWN DATA'
    UNINSURANCED = 1
    ONE = 2  # UPTO 5000
    TWO = 3  # UPTO 10000
    THREE = 4  # UPTO 20000


class ParcelType(ParcelBase):
    """:class:`Enum` that holds parcel types"""
    UNKNOWN = 'UNKNOWN DATA'
    TRACKED = 'Przychodzące'
    SENT = 'Wysłane'
    RETURNS = 'Zwroty'


class ParcelStatus(ParcelBase):
    """:class:`Enum` that holds parcel statuses"""
    UNKNOWN = 'UNKNOWN DATA'
    CREATED = 'Utworzona'  # TODO: translate from app
    OFFERS_PREPARED = 'Oferty przygotowane'  # TODO: translate from app
    OFFER_SELECTED = 'Oferta wybrana'  # TODO: translate from app
    CONFIRMED = 'Potwierdzona'
    READY_TO_PICKUP_FROM_POK = 'Gotowa do odbioru w PaczkoPunkcie'
    OVERSIZED = 'Gabaryt'
    DISPATCHED_BY_SENDER_TO_POK = 'Nadana w PaczkoPunkcie'
    DISPATCHED_BY_SENDER = 'Nadana w paczkomacie'
    COLLECTED_FROM_SENDER = 'Odebrana od nadawcy'
    TAKEN_BY_COURIER = 'Odebrana przez Kuriera'
    ADOPTED_AT_SOURCE_BRANCH = 'Przyjęta w oddziale'
    SENT_FROM_SOURCE_BRANCH = 'Wysłana z oddziału'
    READDRESSED = 'Zmiana punktu dostawy'  # TODO: translate from app
    OUT_FOR_DELIVERY = 'Wydana do doręczenia'
    READY_TO_PICKUP = 'Gotowa do odbioru'
    PICKUP_REMINDER_SENT = 'Wysłano przypomnienie o odbiorze'  # TODO: translate from app
    PICKUP_TIME_EXPIRED = 'Upłynął czas odbioru'  # TODO: translate from app
    AVIZO = 'Powrót do oddziału'
    TAKEN_BY_COURIER_FROM_POK = 'Odebrana z PaczkoPunktu nadawczego'
    REJECTED_BY_RECEIVER = 'Odrzucona przez odbiorcę'  # TODO: translate from app
    UNDELIVERED = 'Nie dostarczona'  # TODO: translate from app
    DELAY_IN_DELIVERY = 'Opóźnienie w dostarczeniu'  # TODO: translate from app
    RETURNED_TO_SENDER = 'Zwrócona do nadawcy'  # TODO: translate from app
    READY_TO_PICKUP_FROM_BRANCH = 'Gotowa do odbioru z oddziału'  # TODO: translate from app
    DELIVERED = 'Doręczona'
    CANCELED = 'Anulowana'  # TODO: translate from app
    CLAIMED = 'Zareklamowana'
    STACK_IN_CUSTOMER_SERVICE_POINT = 'Umieszczona w punkcie obsługi klienta'  # TODO: translate from app
    STACK_PARCEL_PICKUP_TIME_EXPIRED = 'Upłynął czas odbioru'  # TODO: translate from app
    UNSTACK_FROM_CUSTOMER_SERVICE_POINT = '?'  # TODO: translate from app
    COURIER_AVIZO_IN_CUSTOMER_SERVICE_POINT = 'Przekazana do punktu obsługi klienta'  # TODO: translate from app
    TAKEN_BY_COURIER_FROM_CUSTOMER_SERVICE_POINT = 'Odebrana przez kuriera z punktu obsługi klienta'  # TODO: translate from app
    STACK_IN_BOX_MACHINE = 'Paczka w paczkomacie'  # TODO: translate from app
    STACK_PARCEL_IN_BOX_MACHINE_PICKUP_TIME_EXPIRED = 'Upłynął czas odbioru z paczkomatu'  # TODO: translate from app
    UNSTACK_FROM_BOX_MACHINE = 'Odebrana z paczkomatu'  # TODO: translate from app
    ADOPTED_AT_SORTING_CENTER = 'Przyjęta w sortowni'
    OUT_FOR_DELIVERY_TO_ADDRESS = 'Gotowa do doręczenia'
    PICKUP_REMINDER_SENT_ADDRESS = 'Wysłano przypomnienie o odbiorze'  # TODO: translate from app
    UNDELIVERED_WRONG_ADDRESS = 'Nie dostarczono z powodu złego adresu'  # TODO: translate from app
    UNDELIVERED_COD_CASH_RECEIVER = 'Nie dostarczono z powodu nieopłacenia'  # TODO: translate from app
    REDIRECT_TO_BOX = 'Przekierowana do paczkomatu'  # TODO: translate from app
    CANCELED_REDIRECT_TO_BOX = 'Anulowano przekierowanie do paczkomatu'  # TODO: translate from app


class ParcelOwnership(ParcelBase):
    """:class:`Enum` that holds parcel ownership types"""
    UNKNOWN = 'UNKNOWN DATA'
    FRIEND = 'Zaprzyjaźniona'
    OWN = 'Własna'


# both are the same, only for being clear
class CompartmentExpectedStatus(ParcelBase):
    """:class:`Enum` that holds compartment expected statuses"""
    UNKNOWN = 'UNKNOWN DATA'
    OPENED = 'Otwarta'
    CLOSED = 'Zamknięta'


class CompartmentActualStatus(ParcelBase):
    """:class:`Enum` that holds compartment actual statuses"""
    UNKNOWN = 'UNKNOWN DATA'
    OPENED = 'Otwarta'
    CLOSED = 'Zamknięta'


class ParcelServiceName(ParcelBase):
    UNKNOWN = 'UNKNOWN DATA'
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
