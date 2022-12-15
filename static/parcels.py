from enum import Enum
from typing import List, Optional
from arrow import get, arrow


class Parcel:
    def __init__(self, parcel_data: dict):
        self.shipment_number: str = parcel_data['shipmentNumber']
        self.shipment_type: str = parcel_data['shipmentType']
        self._open_code: Optional[str] = parcel_data['openCode'] if 'openCode' in parcel_data else None
        self._qr_code: Optional[str] = parcel_data['qrCode'] if 'qrCode' in parcel_data else None
        self.stored_date: Optional[arrow] = get(parcel_data['storedDate']) if 'storedDate' in parcel_data else None
        self.pickup_date: Optional[arrow] = get(parcel_data['pickUpDate']) if 'pickUpDate' in parcel_data else None
        self.parcel_size: str = parcel_data['parcelSize']
        self.receiver: Receiver = Receiver(receiver_data=parcel_data['receiver'])
        self.sender: Sender = Sender(sender_data=parcel_data['sender'])
        self.pickup_point: PickupPoint = PickupPoint(pickuppoint_data=parcel_data['pickUpPoint'])
        self.is_end_off_week_collection: bool = parcel_data['endOfWeekCollection']
        self.operations: Operations = Operations(operations_data=parcel_data['operations'])
        self.status: str = parcel_data['status']
        self.event_log: List[EventLog] = [EventLog(eventlog_data=event) for event in parcel_data['eventLog']]
        self.avizo_transaction_status: str = parcel_data['avizoTransactionStatus']
        self.shared_to: List[SharedTo] = [SharedTo(sharedto_data=person) for person in parcel_data['sharedTo']]
        self.ownership_status: str = parcel_data['ownershipStatus']

    def __str__(self):
        return f"Shipment number: {self.shipment_number}\n" \
               f"Status: {self.status}\n" \
               f"Pickup point: {self.pickup_point}\n" \
               f"Sender: {str(self.sender)}"


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
        self.type: List[str] = pickuppoint_data['type']
        self.location_round_the_clock: bool = pickuppoint_data['location247']
        self.doubled: bool = pickuppoint_data['doubled']
        self.image_url: str = pickuppoint_data['imageUrl']
        self.easy_access_zone: bool = pickuppoint_data['easyAccessZone']
        self.air_sensor: bool = pickuppoint_data['airSensor']

    def __str__(self):
        return self.name


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
        self.name: str = eventlog_data['name']
        self.date: arrow = get(eventlog_data['date'])


class SharedTo:
    def __init__(self, sharedto_data):
        ...


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
