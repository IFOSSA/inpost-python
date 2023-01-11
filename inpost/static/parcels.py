import random
from io import BytesIO
from typing import List, Tuple

import qrcode
from arrow import get, arrow

from inpost.static.statuses import *


class Parcel:
    def __init__(self, parcel_data: dict):
        self.shipment_number: str = parcel_data['shipmentNumber']
        self.shipment_type: ParcelShipmentType = ParcelShipmentType[parcel_data['shipmentType']]
        self._open_code: str | None = parcel_data['openCode'] if 'openCode' in parcel_data else None
        self._qr_code: QRCode | None = QRCode(parcel_data['qrCode']) if 'qrCode' in parcel_data else None
        self.stored_date: arrow | None = get(parcel_data['storedDate']) if 'storedDate' in parcel_data else None
        self.pickup_date: arrow | None = get(parcel_data['pickUpDate']) if 'pickUpDate' in parcel_data else None
        self.parcel_size: ParcelLockerSize | ParcelCarrierSize = ParcelLockerSize[parcel_data['parcelSize']] \
            if self.shipment_type == ParcelShipmentType.parcel else ParcelCarrierSize[parcel_data['parcelSize']]
        self.receiver: Receiver = Receiver(receiver_data=parcel_data['receiver'])
        self.sender: Sender = Sender(sender_data=parcel_data['sender'])
        self.pickup_point: PickupPoint = PickupPoint(pickuppoint_data=parcel_data['pickUpPoint'])
        self.multi_compartment: MultiCompartment | None = MultiCompartment(parcel_data['multiCompartment']) \
            if 'multiCompartment' in parcel_data else None
        self.is_end_off_week_collection: bool = parcel_data['endOfWeekCollection']
        self.operations: Operations = Operations(operations_data=parcel_data['operations'])
        self.status: ParcelStatus = ParcelStatus[parcel_data['status']]
        self.event_log: List[EventLog] = [EventLog(eventlog_data=event) for event in parcel_data['eventLog']]
        self.avizo_transaction_status: str = parcel_data['avizoTransactionStatus']
        self.shared_to: List[SharedTo] = [SharedTo(sharedto_data=person) for person in parcel_data['sharedTo']]
        self.ownership_status: ParcelOwnership = ParcelOwnership[parcel_data['ownershipStatus']]
        self._compartment_properties: CompartmentProperties | None = None

    def __str__(self):
        return f"Shipment number: {self.shipment_number}\n" \
               f"Status: {self.status}\n" \
               f"Pickup point: {self.pickup_point}\n" \
               f"Sender: {str(self.sender)}"

    @property
    def open_code(self):
        return self._open_code

    @property
    def generate_qr_image(self):
        return self._qr_code.qr_image

    @property
    def compartment_properties(self):
        return self._compartment_properties

    @compartment_properties.setter
    def compartment_properties(self, compartmentproperties_data: dict):
        self._compartment_properties = CompartmentProperties(compartmentproperties_data=compartmentproperties_data)

    @property
    def compartment_location(self):
        return self._compartment_properties.location

    @compartment_location.setter
    def compartment_location(self, location_data):
        self._compartment_properties.location = location_data

    @property
    def compartment_status(self):
        return self._compartment_properties.status

    @compartment_status.setter
    def compartment_status(self, status):
        self._compartment_properties.status = status

    @property
    def compartment_open_data(self):
        return {
            'shipmentNumber': self.shipment_number,
            'openCode': self._open_code,
            'receiverPhoneNumber': self.receiver.phone_number
        }

    @property
    def mocked_location(self):
        return {
            'latitude': round(self.pickup_point.latitude + random.uniform(-0.00005, 0.00005), 6),
            'longitude': round(self.pickup_point.longitude + random.uniform(-0.00005, 0.00005), 6),
            'accuracy': round(random.uniform(1, 4), 1)
        }


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
        self.shipment_numbers: List[str] | None = multicompartment_data['shipmentNumbers'] \
            if 'shipmentNumbers' in multicompartment_data else None
        self.presentation: bool = multicompartment_data['presentation']
        self.collected: bool = multicompartment_data['collected']


class Operations:
    def __init__(self, operations_data):
        self.manual_archive: bool = operations_data['manualArchive']
        self.auto_archivable_since: arrow | None = get(
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


class CompartmentLocation:
    def __init__(self, compartmentlocation_data: dict):
        self.name: str = compartmentlocation_data['compartment']['name']
        self.side: str = compartmentlocation_data['compartment']['location']['side']
        self.column: str = compartmentlocation_data['compartment']['location']['column']
        self.row: str = compartmentlocation_data['compartment']['location']['row']
        self.open_compartment_waiting_time: int = compartmentlocation_data['openCompartmentWaitingTime']
        self.action_time: int = compartmentlocation_data['actionTime']
        self.confirm_action_time: int = compartmentlocation_data['confirmActionTime']


class CompartmentProperties:
    def __init__(self, compartmentproperties_data: dict):
        self._session_uuid: str = compartmentproperties_data['sessionUuid']
        self._session_expiration_time: int = compartmentproperties_data['sessionExpirationTime']
        self._location: CompartmentLocation | None = None
        self._status: CompartmentActualStatus | None = None

    @property
    def session_uuid(self):
        return self._session_uuid

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location_data: dict):
        self._location = CompartmentLocation(location_data)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status_data: str | CompartmentActualStatus):
        self._status = status_data if isinstance(status_data, CompartmentActualStatus) \
            else CompartmentActualStatus[status_data]
