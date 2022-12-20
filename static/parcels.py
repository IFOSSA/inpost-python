from enum import Enum
from io import BytesIO
from typing import List, Optional, Tuple, Union

import qrcode
from arrow import get, arrow


class Parcel:
    def __init__(self, parcel_data: dict):
        self.shipment_number: str = parcel_data['shipmentNumber']
        self.shipment_type: ParcelShipmentType = ParcelShipmentType[parcel_data['shipmentType']]
        self._open_code: Optional[str] = parcel_data['openCode'] if 'openCode' in parcel_data else None
        self._qr_code: Optional[QRCode] = QRCode(parcel_data['qrCode']) if 'qrCode' in parcel_data else None
        self.stored_date: Optional[arrow] = get(parcel_data['storedDate']) if 'storedDate' in parcel_data else None
        self.pickup_date: Optional[arrow] = get(parcel_data['pickUpDate']) if 'pickUpDate' in parcel_data else None
        self.parcel_size: Union[ParcelLockerSize, ParcelCarrierSize] = ParcelLockerSize[parcel_data['parcelSize']] \
            if self.shipment_type == ParcelShipmentType.parcel else ParcelCarrierSize[parcel_data['parcelSize']]
        self.receiver: Receiver = Receiver(receiver_data=parcel_data['receiver'])
        self.sender: Sender = Sender(sender_data=parcel_data['sender'])
        self.pickup_point: PickupPoint = PickupPoint(pickuppoint_data=parcel_data['pickUpPoint'])
        self.multi_compartment: Optional[MultiCompartment] = MultiCompartment(parcel_data['multiCompartment']) \
            if 'multiCompartment' in parcel_data else None
        self.is_end_off_week_collection: bool = parcel_data['endOfWeekCollection']
        self.operations: Operations = Operations(operations_data=parcel_data['operations'])
        self.status: ParcelStatus = ParcelStatus[parcel_data['status']]
        self.event_log: List[EventLog] = [EventLog(eventlog_data=event) for event in parcel_data['eventLog']]
        self.avizo_transaction_status: str = parcel_data['avizoTransactionStatus']
        self.shared_to: List[SharedTo] = [SharedTo(sharedto_data=person) for person in parcel_data['sharedTo']]
        self.ownership_status: ParcelOwnership = ParcelOwnership[parcel_data['ownershipStatus']]

    def __str__(self):
        return f"Shipment number: {self.shipment_number}\n" \
               f"Status: {self.status}\n" \
               f"Pickup point: {self.pickup_point}\n" \
               f"Sender: {str(self.sender)}"

    @property
    def generate_qr_image(self):
        return self._qr_code.qr_image


class Receiver:
    def __init__(self, receiver_data: dict):
        self.email: str = receiver_data['email']
        self.phone_number: str = receiver_data['phoneNumber']
        self.name: str = receiver_data['name']


class Sender:
    def __init__(self, sender_data: dict):
        self.sender_name: str = sender_data['name']

    def __str__(self):
        return self.sender_name


class PickupPoint:
    def __init__(self, pickuppoint_data):
        self.name: str = pickuppoint_data['name']
        self.latitude: float = pickuppoint_data['location']['latitude']
        self.longitude: float = pickuppoint_data['location']['longitude']
        self.description: str = pickuppoint_data['locationDescription']
        self.opening_hours: str = pickuppoint_data['openingHours']
        self.post_code: str = pickuppoint_data['addressDetails']['postCode']
        self.city: str = pickuppoint_data['addressDetails']['city']
        self.province: str = pickuppoint_data['addressDetails']['province']
        self.street: str = pickuppoint_data['addressDetails']['street']
        self.building_number: str = pickuppoint_data['addressDetails']['buildingNumber']
        self.virtual: int = pickuppoint_data['virtual']
        self.point_type: str = pickuppoint_data['pointType']
        self.type: List[ParcelDeliveryType] = [ParcelDeliveryType[data] for data in pickuppoint_data['type']]
        self.location_round_the_clock: bool = pickuppoint_data['location247']
        self.doubled: bool = pickuppoint_data['doubled']
        self.image_url: str = pickuppoint_data['imageUrl']
        self.easy_access_zone: bool = pickuppoint_data['easyAccessZone']
        self.air_sensor: bool = pickuppoint_data['airSensor']

    def __str__(self):
        return self.name

    @property
    def location(self) -> Tuple[float, float]:
        return self.latitude, self.longitude


class MultiCompartment:
    def __init__(self, multicompartment_data):
        self.uuid = multicompartment_data['uuid']
        self.shipment_numbers: Optional[List['str']] = multicompartment_data['shipmentNumbers'] \
            if 'shipmentNumbers' in multicompartment_data else None
        self.presentation: bool = multicompartment_data['presentation']
        self.collected: bool = multicompartment_data['collected']


class Operations:
    def __init__(self, operations_data):
        self.manual_archive: bool = operations_data['manualArchive']
        self.auto_archivable_since: Optional[arrow] = get(
            operations_data['autoArchivableSince']) if 'autoArchivableSince' in operations_data else None
        self.delete: bool = operations_data['delete']
        self.collect: bool = operations_data['collect']
        self.expand_avizo: bool = operations_data['expandAvizo']
        self.highlight: bool = operations_data['highlight']
        self.refresh_until: arrow = get(operations_data['refreshUntil'])
        self.request_easy_access_zone: str = operations_data['requestEasyAccessZone']
        self.is_voicebot: bool = operations_data['voicebot']
        self.can_share_to_observe: bool = operations_data['canShareToObserve']
        self.can_share_open_code: bool = operations_data['canShareOpenCode']
        self.can_share_parcel: bool = operations_data['canShareParcel']


class EventLog:
    def __init__(self, eventlog_data: dict):
        self.type: str = eventlog_data['type']
        self.name: ParcelStatus = ParcelStatus[eventlog_data['name']]
        self.date: arrow = get(eventlog_data['date'])


class SharedTo:
    def __init__(self, sharedto_data):
        self.uuid: str = sharedto_data['uuid']
        self.name: str = sharedto_data['name']
        self.phone_number = sharedto_data['phoneNumber']


class QRCode:
    def __init__(self, qrcode_data: str):
        self._qr_code = qrcode_data

    @property
    def qr_image(self) -> BytesIO:
        qr = qrcode.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=4,
            mask_pattern=5
        )

        qr.add_data(self._qr_code)
        qr.make(fit=False)
        img1 = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        bio.name = 'qr.png'
        img1.save(bio, 'PNG')
        bio.seek(0)
        return bio


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


class ParcelLockerSize(ParcelBase):
    A = '8x38x64'
    B = '19x38x64'
    C = '41x38x64'


class ParcelDeliveryType(ParcelBase):
    parcel_locker = 'Paczkomat'
    carrier = 'Kurier'
    parcel_point = 'PaczkoPunkt'


class ParcelShipmentType(ParcelBase):
    parcel = 'Paczkomat'
    carrier = 'Kurier'
    parcel_point = 'PaczkoPunkt'


class ParcelAdditionalInsurance(ParcelBase):
    UNINSURANCED = 1
    ONE = 2  # UPTO 5000
    TWO = 3  # UPTO 10000
    THREE = 4  # UPTO 20000


class ParcelForm(ParcelBase):
    OUTGOING = 1
    INCOMING = 2


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
    READY_TO_PICKUP = 'Gotowa do odbioru'
    DELIVERED = 'Doręczona'


class ParcelOwnership(ParcelBase):
    FRIEND = 'Zaprzyjaźniona'
    OWN = 'Własna'


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
