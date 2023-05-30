import logging
import random
from io import BytesIO
from typing import List, Tuple

import qrcode
from arrow import get, arrow

from inpost.static.statuses import *


class BaseParcel:
    def __init__(self, parcel_data: dict, logger: logging.Logger):
        self.shipment_number: str = parcel_data.get('shipmentNumber')
        self._log: logging.Logger = logger.getChild(f'{__class__.__name__}.{self.shipment_number}')
        self.status: ParcelStatus = ParcelStatus[parcel_data['status']]
        self.expiry_date: arrow | None = get(parcel_data['expiryDate']) if 'expiryDate' in parcel_data else None
        self.operations: Operations = Operations(operations_data=parcel_data['operations'], logger=self._log)
        self.event_log: List[EventLog] = [EventLog(eventlog_data=event, logger=self._log)
                                          for event in parcel_data['eventLog']]


class Parcel(BaseParcel):
    """Object representation of :class:`inpost.api.Inpost` compartment properties

    :param parcel_data: :class:`dict` containing all parcel data
    :type parcel_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, parcel_data: dict, logger: logging.Logger):
        """Constructor method"""
        super().__init__(parcel_data, logger)
        self._log: logging.Logger = logger.getChild(f'{__class__.__name__}.{self.shipment_number}')
        self.shipment_type: ParcelShipmentType = ParcelShipmentType[parcel_data['shipmentType']]
        self._open_code: str | None = parcel_data.get('openCode', None)
        self._qr_code: QRCode | None = QRCode(qrcode_data=parcel_data['qrCode'], logger=self._log) \
            if 'qrCode' in parcel_data else None
        self.stored_date: arrow | None = get(parcel_data['storedDate']) if 'storedDate' in parcel_data else None
        self.pickup_date: arrow | None = get(parcel_data['pickUpDate']) if 'pickUpDate' in parcel_data else None
        self.parcel_size: ParcelLockerSize | ParcelCarrierSize = ParcelLockerSize[parcel_data['parcelSize']] \
            if self.shipment_type == ParcelShipmentType.parcel else ParcelCarrierSize[parcel_data['parcelSize']]
        self.receiver: Receiver = Receiver(receiver_data=parcel_data['receiver'], logger=self._log) if 'reveiver' in parcel_data else None
        self.sender: Sender = Sender(sender_data=parcel_data['sender'], logger=self._log) if 'sender' in parcel_data else None
        self.pickup_point: PickupPoint = PickupPoint(pickuppoint_data=parcel_data['pickUpPoint'], logger=self._log) \
            if 'pickUpPoint' in parcel_data else None
        self.multi_compartment: MultiCompartment | None = MultiCompartment(
            parcel_data['multiCompartment'], logger=self._log) if 'multiCompartment' in parcel_data else None
        self.is_end_off_week_collection: bool | None = parcel_data.get('endOfWeekCollection', None)
        self.status: ParcelStatus = ParcelStatus[parcel_data['status']] if 'status' in parcel_data else None
        self.avizo_transaction_status: str | None = parcel_data.get('avizoTransactionStatus', None)
        self.shared_to: List[SharedTo] = [SharedTo(sharedto_data=person, logger=self._log)
                                          for person in parcel_data['sharedTo']] if 'sharedTo' in parcel_data else None
        self.ownership_status: ParcelOwnership = ParcelOwnership[parcel_data['ownershipStatus']] if 'ownershipStatus' in parcel_data else None
        self.economy_parcel: bool | None = parcel_data.get('economyParcel', None)
        self._compartment_properties: CompartmentProperties | None = None

        self._log.debug(f'created parcel with shipment number {self.shipment_number}')

        # log all unexpected things, so you can make an issue @github
        if self.shipment_type == ParcelShipmentType.UNKNOWN:
            self._log.debug(f'unexpected shipment_type: {parcel_data["shipmentType"]}')

        if self.parcel_size == ParcelCarrierSize.UNKNOWN or self.parcel_size == ParcelLockerSize.UNKNOWN:
            self._log.debug(f'unexpected parcel_size: {parcel_data["parcelSize"]}')

        if self.status == ParcelStatus.UNKNOWN:
            self._log.debug(f'unexpected parcel status: {parcel_data["status"]}')

        if self.ownership_status == ParcelOwnership.UNKNOWN:
            self._log.debug(f'unexpected ownership status: {parcel_data["ownershipStatus"]}')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")

    def __str__(self):
        return f"Sender: {str(self.sender)}\n" \
               f"Shipment number: {self.shipment_number}\n" \
               f"Status: {self.status}\n" \
               f"Pickup point: {self.pickup_point}"

    @property
    def open_code(self) -> str | None:
        """Returns an open code for :class:`Parcel`

        :return: Open code for :class:`Parcel`
        :rtype: str"""
        self._log.debug('getting open code')
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug('got open code')
            return self._open_code

        self._log.debug(f'wrong ParcelShipmentType: {repr(self.shipment_type)}')
        return None

    @property
    def generate_qr_image(self) -> BytesIO | None:
        """Returns a QR image for :class:`Parcel`

        :return: QR image for :class:`Parcel`
        :rtype: BytesIO"""
        self._log.debug('generating qr image')
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug('got qr image')
            return self._qr_code.qr_image

        self._log.debug(f'wrong ParcelShipmentType: {repr(self.shipment_type)}')
        return None

    @property
    def compartment_properties(self):
        """Returns a compartment properties for :class:`Parcel`

        :return: Compartment properties for :class:`Parcel`
        :rtype: CompartmentProperties"""
        self._log.debug('getting comparment properties')
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug('got compartment properties')
            return self._compartment_properties

        self._log.debug(f'wrong ParcelShipmentType: {repr(self.shipment_type)}')
        return None

    @compartment_properties.setter
    def compartment_properties(self, compartmentproperties_data: dict):
        """Set compartment properties for :class:`Parcel`

        :param compartmentproperties_data: :class:`dict` containing compartment properties data for :class:`Parcel`
        :type compartmentproperties_data: CompartmentProperties"""
        self._log.debug(f'setting compartment properties with {compartmentproperties_data}')
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug('compartment properties set')
            self._compartment_properties = CompartmentProperties(compartmentproperties_data=compartmentproperties_data,
                                                                 logger=self._log)

        self._log.debug(f'wrong ParcelShipmentType: {repr(self.shipment_type)}')

    @property
    def compartment_location(self):
        """Returns a compartment location for :class:`Parcel`

        :return: Compartment location for :class:`Parcel`
        :rtype: CompartmentLocation"""
        self._log.debug('getting compartment location')
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug('got compartment location')
            return self._compartment_properties.location if self._compartment_properties else None

        self._log.debug(f'wrong ParcelShipmentType: {repr(self.shipment_type)}')
        return None

    @compartment_location.setter
    def compartment_location(self, location_data: dict):
        """Set compartment location for :class:`Parcel`
        :param location_data: :class:`dict` containing `compartment properties` data for :class:`Parcel`
        :type location_data: CompartmentProperties"""
        self._log.debug(f'setting compartment location with {location_data}')
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug('compartment location set')
            self._compartment_properties.location = location_data

        self._log.debug(f'wrong ParcelShipmentType: {repr(self.shipment_type)}')

    @property
    def compartment_status(self) -> CompartmentActualStatus | None:
        """Returns a compartment status for :class:`Parcel`

        :return: Compartment status for :class:`Parcel`
        :rtype: CompartmentActualStatus"""
        self._log.debug('getting compartment status')

        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug('got compartment status')
            return self._compartment_properties.status if self._compartment_properties else None

        self._log.debug(f'wrong ParcelShipmentType: {repr(self.shipment_type)}')
        return None

    @compartment_status.setter
    def compartment_status(self, status):
        self._log.debug(f'setting compartment status with {status}')
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug('compartment status set')
            self._compartment_properties.status = status

        self._log.debug(f'wrong ParcelShipmentType: {repr(self.shipment_type)}')

    @property
    def compartment_open_data(self):
        """Returns a compartment open data for :class:`Parcel`

        :return: dict containing compartment open data for :class:`Parcel`
        :rtype: dict"""
        self._log.debug('getting compartment open data')
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug('got compartment open data')
            return {
                'shipmentNumber': self.shipment_number,
                'openCode': self._open_code,
                'receiverPhoneNumber': self.receiver.phone_number
            }

        self._log.debug(f'wrong ParcelShipmentType: {repr(self.shipment_type)}')
        return None

    @property
    def mocked_location(self):
        """Returns a mocked location for :class:`Parcel`

        :return: dict containing mocked location for :class:`Parcel`
        :rtype: dict"""
        self._log.debug('getting mocked location')
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug('got mocked location')
            return {
                'latitude': round(self.pickup_point.latitude + random.uniform(-0.00005, 0.00005), 6),
                'longitude': round(self.pickup_point.longitude + random.uniform(-0.00005, 0.00005), 6),
                'accuracy': round(random.uniform(1, 4), 1)
            }

        self._log.debug(f'wrong ParcelShipmentType: {repr(self.shipment_type)}')
        return None

    @property
    def is_multicompartment(self):
        """Specifies if parcel is in multi compartment
        :return: True if parcel is in multicompartment
        :rtype: bool"""
        return self.multi_compartment is not None

    @property
    def is_main_multicompartment(self):
        """Specifies if parcel is main parcel in multi compartment
        :return: True if parcel is in multicompartment
        :rtype: bool"""
        if self.is_multicompartment:
            return self.multi_compartment.shipment_numbers is not None

        return None

    # @property
    # def get_from_multicompartment(self):
    #     return


class ReturnParcel(BaseParcel):
    def __init__(self, parcel_data: dict, logger: logging.Logger):
        super().__init__(parcel_data, logger)
        self.uuid: str = parcel_data['uuid']
        self.rma: str = parcel_data['rma']
        self.organization_name: str = parcel_data['organizationName']
        self.created_date: arrow = parcel_data['createdDate']
        self.accepted_date: arrow = parcel_data['acceptedDate']
        self.expiry_date: arrow = parcel_data['expiryDate']
        self.sent_date: arrow = parcel_data['sentDate']
        self.delivered_date: arrow = parcel_data['deliveredDate']
        self.order_number: str = parcel_data['orderNumber']
        self.form_type: str = parcel_data['formType']


class Receiver:
    """Object representation of :class:`Parcel` receiver

    :param receiver_data: :class:`dict` containing sender data for :class:`Parcel`
    :type receiver_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, receiver_data: dict, logger: logging.Logger):
        """Constructor method"""
        self.email: str = receiver_data['email']
        self.phone_number: str = receiver_data['phoneNumber']
        self.name: str = receiver_data['name']
        self._log: logging.Logger = logger.getChild(__class__.__name__)

        self._log.debug('created')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")


class Sender:
    """Object representation of :class:`Parcel` sender

    :param sender_data: :class:`dict` containing sender data for :class:`Parcel`
    :type sender_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, sender_data: dict, logger: logging.Logger):
        """Constructor method"""
        self.sender_name: str = sender_data['name']
        self._log: logging.Logger = logger.getChild(__class__.__name__)

        self._log.debug('created')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")

    def __str__(self) -> str:
        return self.sender_name


class PickupPoint:
    """Object representation of :class:`Parcel` pickup point

    :param pickuppoint_data: :class:`dict` containing pickup point data for :class:`Parcel`
    :type pickuppoint_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, pickuppoint_data: dict, logger: logging.Logger):
        """Constructor method"""
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
        self.air_sensor_data: AirSensorData | None = AirSensorData(pickuppoint_data['airSensorData']) if 'airSensorData' in pickuppoint_data else None

        self._log: logging.Logger = logger.getChild(__class__.__name__)
        self._log.debug('created')

        if ParcelDeliveryType.UNKNOWN in self.type:
            self._log.debug(f'unknown delivery type: {pickuppoint_data["type"]}')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")

    def __str__(self) -> str:
        return self.name

    @property
    def location(self) -> Tuple[float, float]:
        """Returns a mocked location for :class:`PickupPoint`

        :return: tuple containing location for :class:`PickupPoint`
        :rtype: tuple"""
        self._log.debug('getting location')
        return self.latitude, self.longitude


class MultiCompartment:
    """Object representation of :class:`Parcel` `multicompartment`

    :param multicompartment_data: :class:`dict` containing multicompartment data for :class:`Parcel`
    :type multicompartment_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, multicompartment_data: dict, logger: logging.Logger):
        """Constructor method"""
        self.uuid = multicompartment_data['uuid']
        self.shipment_numbers: List[str] | None = multicompartment_data['shipmentNumbers'] \
            if 'shipmentNumbers' in multicompartment_data else None
        self.presentation: bool = multicompartment_data['presentation']
        self.collected: bool = multicompartment_data['collected']

        self._log: logging.Logger = logger.getChild(__class__.__name__)
        self._log.debug('created')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")


class Operations:
    """Object representation of :class:`Parcel` `operations`

    :param operations_data: :class:`dict` containing operations data for :class:`Parcel`
    :type operations_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, operations_data: dict, logger: logging.Logger):
        """Constructor method"""
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
        self.send: bool | None = operations_data['send'] if 'send' in operations_data else None

        self._log: logging.Logger = logger.getChild(__class__.__name__)
        self._log.debug('created')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")


class EventLog:
    """Object representation of :class:`Parcel` single eventlog

    :param eventlog_data: :class:`dict` containing single eventlog data for :class:`Parcel`
    :type eventlog_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, eventlog_data: dict, logger: logging.Logger):
        """Constructor method"""
        self.type: str = eventlog_data['type']
        self.name: ParcelStatus | ReturnsStatus = ParcelStatus[
            eventlog_data['name']] if self.type == 'PARCEL_STATUS' else ReturnsStatus[eventlog_data['name']]
        self.date: arrow = get(eventlog_data['date'])

        self._log: logging.Logger = logger.getChild(__class__.__name__)
        self._log.debug('created')

        if self.name == ParcelStatus.UNKNOWN or self.name == ReturnsStatus.UNKNOWN:
            self._log.debug(f'unknown {self.type}: {eventlog_data["name"]}')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")


class SharedTo:
    """Object representation of :class:`Parcel` single shared to

    :param sharedto_data: :class:`dict` containing shared to data for :class:`Parcel`
    :type sharedto_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, sharedto_data: dict, logger: logging.Logger):
        """Constructor method"""
        self.uuid: str = sharedto_data['uuid']
        self.name: str = sharedto_data['name']
        self.phone_number = sharedto_data['phoneNumber']

        self._log: logging.Logger = logger.getChild(__class__.__name__)
        self._log.debug('created')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")


class QRCode:
    """Object representation of :class:`Parcel` QRCode

    :param qrcode_data: :class:`str` containing qrcode data for :class:`Parcel`
    :type qrcode_data: str
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, qrcode_data: str, logger: logging.Logger):
        """Constructor method"""
        self._qr_code = qrcode_data

        self._log: logging.Logger = logger.getChild(__class__.__name__)
        self._log.debug('created')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")

    @property
    def qr_image(self) -> BytesIO:
        """Returns a generated QR image for :class:`QRCode`

        :return: QR Code image
        :rtype: BytesIO"""
        self._log.debug('generating qr image')
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
        self._log.debug('generated qr image')
        return bio


class CompartmentLocation:
    """Object representation of :class:`CompartmentProperties` compartment location

    :param compartmentlocation_data: :class:`dict` containing compartment location data for :class:`Parcel`
    :type compartmentlocation_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, compartmentlocation_data: dict, logger: logging.Logger):
        """Constructor method"""
        self.name: str = compartmentlocation_data['compartment']['name']
        self.side: str = compartmentlocation_data['compartment']['location']['side']
        self.column: str = compartmentlocation_data['compartment']['location']['column']
        self.row: str = compartmentlocation_data['compartment']['location']['row']
        self.open_compartment_waiting_time: int = compartmentlocation_data['openCompartmentWaitingTime']
        self.action_time: int = compartmentlocation_data['actionTime']
        self.confirm_action_time: int = compartmentlocation_data['confirmActionTime']

        self._log: logging.Logger = logger.getChild(__class__.__name__)
        self._log.debug('created')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")


class CompartmentProperties:
    """Object representation of :class:`Parcel` compartment properties

    :param compartmentproperties_data: :class:`dict` containing compartment properties data for :class:`Parcel`
    :type compartmentproperties_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, compartmentproperties_data: dict, logger: logging.Logger):
        """Constructor method"""
        self._session_uuid: str = compartmentproperties_data['sessionUuid']
        self._session_expiration_time: int = compartmentproperties_data['sessionExpirationTime']
        self._location: CompartmentLocation | None = None
        self._status: CompartmentActualStatus | None = None

        self._log: logging.Logger = logger.getChild(__class__.__name__)
        self._log.debug('created')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")

    @property
    def session_uuid(self):
        """Returns a session unique identified for :class:`CompartmentProperties`

        :return: string containing session unique identified for :class:`CompartmentProperties`
        :rtype: str"""
        self._log.debug('getting session uuid')
        return self._session_uuid

    @property
    def location(self):
        """Returns a compartment location for :class:`CompartmentProperties`

        :return: compartment location for :class:`CompartmentProperties`
        :rtype: str"""
        self._log.debug('getting location')
        return self._location

    @location.setter
    def location(self, location_data: dict):
        """Set a compartment location for :class:`CompartmentProperties`

        :param location_data: dict containing compartment location data for :class:`CompartmentProperties`
        :type location_data: dict"""
        self._log.debug('setting location')
        self._location = CompartmentLocation(location_data, self._log)

    @property
    def status(self):
        """Returns a compartment status for :class:`CompartmentProperties`

        :return: compartment location for :class:`CompartmentProperties`
        :rtype: CompartmentActualStatus"""
        self._log.debug('getting status')
        return self._status

    @status.setter
    def status(self, status_data: str | CompartmentActualStatus):
        self._log.debug('setting status')
        self._status = status_data if isinstance(status_data, CompartmentActualStatus) \
            else CompartmentActualStatus[status_data]

        if self._status == CompartmentActualStatus.UNKNOWN and isinstance(status_data, str):
            self._log.debug(f'unexpected compartment actual status: {status_data}')


class AirSensorData:
    """Object representation of :class:`Parcel` air sensor data

    :param airsensor_data: :class:`dict` containing air sensor data for :class:`Parcel`
    :type airsensor_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""
    def __init__(self, airsensor_data: dict, logger: logging.Logger):
        self.updated_until: arrow = airsensor_data['updatedUntil']
        self.air_quality: str = airsensor_data['airQuality']
        self.temperature: float = airsensor_data['temperature']
        self.humidity: float = airsensor_data['humidity']
        self.pressure: float = airsensor_data['pressure']
        self.pm25_value: float = airsensor_data['pollutants']['pm25']['value']
        self.pm25_percent: float = airsensor_data['pollutants']['pm25']['percent']
        self.pm10_value: float = airsensor_data['pollutants']['pm10']['value']
        self.pm10_percent: float = airsensor_data['pollutants']['pm10']['percent']

        self._log: logging.Logger = logger.getChild(__class__.__name__)
        self._log.debug('created')
