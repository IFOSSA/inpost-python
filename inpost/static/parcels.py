import logging
import random
from io import BytesIO
from typing import List, Tuple

import qrcode
from arrow import arrow, get

from inpost.static.exceptions import UnknownStatusError
from inpost.static.statuses import (
    CompartmentActualStatus,
    ParcelCarrierSize,
    ParcelDeliveryType,
    ParcelLockerSize,
    ParcelOwnership,
    ParcelShipmentType,
    ParcelStatus,
    PaymentStatus,
    PaymentType,
    PointType,
    ReturnsStatus,
)


class BaseParcel:
    """Object representation of :class:`inpost.api.Inpost` parcel base. Gather things shared by all parcel types.

    :param parcel_data: :class:`dict` containing all parcel data
    :type parcel_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, parcel_data: dict, logger: logging.Logger):
        self.shipment_number = parcel_data.get("shipmentNumber")
        self._log: logging.Logger = logger.getChild(f"{self.__class__.__name__}.{self.shipment_number}")
        self.status: ParcelStatus = ParcelStatus[parcel_data.get("status")]
        self.expiry_date: arrow | None = get(parcel_data["expiryDate"]) if "expiryDate" in parcel_data else None
        self.operations: Operations = Operations(operations_data=parcel_data["operations"], logger=self._log)
        self.event_log: List[EventLog] = [
            EventLog(eventlog_data=event, logger=self._log) for event in parcel_data["eventLog"]
        ]


class Parcel(BaseParcel):
    """Object representation of :class:`inpost.api.Inpost` incoming parcel

    :param parcel_data: :class:`dict` containing all parcel data
    :type parcel_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, parcel_data: dict, logger: logging.Logger):
        """Constructor method

        :param parcel_data: dict containing parcel data
        :type parcel_data: dict
        :param logger: logger instance
        :type logger: logging.Logger
        """

        super().__init__(parcel_data, logger)
        self._log: logging.Logger = logger.getChild(f"{self.__class__.__name__}.{self.shipment_number}")
        self.shipment_type: ParcelShipmentType = ParcelShipmentType[parcel_data.get("shipmentType")]
        self._open_code: str | None = parcel_data.get("openCode", None)
        self._qr_code: QRCode | None = (
            QRCode(qrcode_data=parcel_data["qrCode"], logger=self._log) if "qrCode" in parcel_data else None
        )
        self.stored_date: arrow | None = get(parcel_data["storedDate"]) if "storedDate" in parcel_data else None
        self.pickup_date: arrow | None = get(parcel_data["pickUpDate"]) if "pickUpDate" in parcel_data else None
        self.parcel_size: ParcelLockerSize | ParcelCarrierSize = (
            ParcelLockerSize[parcel_data.get("parcelSize")]
            if self.shipment_type == ParcelShipmentType.parcel
            else ParcelCarrierSize[parcel_data.get("parcelSize")]
        )
        self.receiver: Receiver | None = (
            Receiver(receiver_data=parcel_data["receiver"], logger=self._log) if "receiver" in parcel_data else None
        )
        self.sender: Sender | None = (
            Sender(sender_data=parcel_data["sender"], logger=self._log) if "sender" in parcel_data else None
        )
        self.pickup_point: PickupPoint | None = (
            PickupPoint(point_data=parcel_data["pickUpPoint"], logger=self._log)
            if "pickUpPoint" in parcel_data
            else None
        )
        self.multi_compartment: MultiCompartment | None = (
            MultiCompartment(parcel_data["multiCompartment"], logger=self._log)
            if "multiCompartment" in parcel_data
            else None
        )

        self.is_end_off_week_collection: bool | None = parcel_data.get("endOfWeekCollection", None)
        self.status: ParcelStatus | None = ParcelStatus[parcel_data.get("status")]
        self.avizo_transaction_status: str | None = parcel_data.get("avizoTransactionStatus", None)
        self.shared_to: List[SharedTo] | None = (
            [SharedTo(sharedto_data=person, logger=self._log) for person in parcel_data["sharedTo"]]
            if "sharedTo" in parcel_data
            else None
        )
        self.ownership_status: ParcelOwnership | None = ParcelOwnership[parcel_data.get("ownershipStatus")]
        self.economy_parcel: bool | None = parcel_data.get("economyParcel", None)
        self._compartment_properties: CompartmentProperties | None = None

        self._log.debug(f"created parcel with shipment number {self.shipment_number}")

        # log all unexpected things, so you can make an issue @github
        if self.shipment_type == ParcelShipmentType.UNKNOWN:
            self._log.warning(f'unexpected shipment_type: {parcel_data["shipmentType"]}')

        if self.parcel_size == ParcelCarrierSize.UNKNOWN or self.parcel_size == ParcelLockerSize.UNKNOWN:
            self._log.warning(f'unexpected parcel_size: {parcel_data["parcelSize"]}')

        if self.status == ParcelStatus.UNKNOWN:
            self._log.warning(f'unexpected parcel status: {parcel_data["status"]}')

        if self.ownership_status == ParcelOwnership.UNKNOWN:
            self._log.warning(f'unexpected ownership status: {parcel_data["ownershipStatus"]}')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")

    def __str__(self):
        return (
            f"Sender: {str(self.sender)}\n"
            f"Shipment number: {self.shipment_number}\n"
            f"Status: {self.status}\n"
            f"Pickup point: {self.pickup_point}"
        )

    @property
    def open_code(self) -> str | None:
        """Returns an open code for :class:`Parcel`

        :return: Open code for :class:`Parcel`
        :rtype: str
        """

        self._log.debug("getting open code")
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("got open code")
            return self._open_code

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return None

    @property
    def generate_qr_image(self) -> BytesIO | None:
        """Returns a QR image for :class:`Parcel`

        :return: QR image for :class:`Parcel`
        :rtype: BytesIO
        """

        self._log.debug("generating qr image")
        if self.shipment_type == ParcelShipmentType.parcel and self._qr_code is not None:
            self._log.debug("got qr image")
            return self._qr_code.qr_image

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return None

    @property
    def compartment_properties(self):
        """Returns a compartment properties for :class:`Parcel`

        :return: Compartment properties for :class:`Parcel`
        :rtype: CompartmentProperties
        """

        self._log.debug("getting comparment properties")
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("got compartment properties")
            return self._compartment_properties

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return None

    @compartment_properties.setter
    def compartment_properties(self, compartmentproperties_data: dict):
        """Set compartment properties for :class:`Parcel`

        :param compartmentproperties_data: :class:`dict` containing compartment properties data for :class:`Parcel`
        :type compartmentproperties_data: dict
        """

        self._log.debug(f"setting compartment properties with {compartmentproperties_data}")
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("compartment properties set")
            self._compartment_properties = CompartmentProperties(
                compartmentproperties_data=compartmentproperties_data, logger=self._log
            )
            return

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")

    @property
    def compartment_location(self):
        """Returns a compartment location for :class:`Parcel`

        :return: Compartment location for :class:`Parcel`
        :rtype: CompartmentLocation
        """

        self._log.debug("getting compartment location")
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("got compartment location")
            return self._compartment_properties.location if self._compartment_properties else None

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return None

    @compartment_location.setter
    def compartment_location(self, location_data: dict):
        """Set compartment location for :class:`Parcel`

        :param location_data: :class:`dict` containing `compartment properties` data for :class:`Parcel`
        :type location_data: dict
        """

        self._log.debug(f"setting compartment location with {location_data}")
        if self.shipment_type == ParcelShipmentType.parcel and self._compartment_properties is not None:
            self._log.debug("compartment location set")
            self._compartment_properties.location = location_data
            return

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")

    @property
    def compartment_status(self) -> CompartmentActualStatus | None:
        """Returns a compartment status for :class:`Parcel`

        :return: Compartment status for :class:`Parcel`
        :rtype: CompartmentActualStatus
        """

        self._log.debug("getting compartment status")

        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("got compartment status")
            return self._compartment_properties.status if self._compartment_properties else None

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return None

    @compartment_status.setter
    def compartment_status(self, status) -> None:
        """Set compartment location for :class:`SentParcel`

        :param status: compartment properties status for :class:`SentParcel`
        :type status: str | CompartmentActualStatus
        """

        self._log.debug(f"setting compartment status with {status}")
        if self._compartment_properties is None:
            self._log.warning("tried to assign status to empty _compartment_properties")
            return

        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("compartment status set")
            self._compartment_properties.status = status
            return

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")

    @property
    def compartment_open_data(self) -> dict:
        """Returns a compartment open data for :class:`Parcel`

        :return: dict containing compartment open data for :class:`Parcel`
        :rtype: dict
        """

        self._log.debug("getting compartment open data")
        if self.receiver is None:
            return {}

        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("got compartment open data")
            return {
                "shipmentNumber": self.shipment_number,
                "openCode": self._open_code,
            }

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return {}

    @property
    def mocked_location(self) -> dict | None:
        """Returns a mocked location for :class:`Parcel`

        :return: dict containing mocked location for :class:`Parcel or None if wrong parcel shipment type`
        :rtype: dict | None
        """

        self._log.debug("getting mocked location")
        if self.pickup_point is None:
            return None
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("got mocked location")
            return {
                "latitude": round(self.pickup_point.latitude + random.uniform(-0.00005, 0.00005), 6),
                "longitude": round(self.pickup_point.longitude + random.uniform(-0.00005, 0.00005), 6),
                "accuracy": round(random.uniform(1, 4), 1),
            }

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return None

    @property
    def is_multicompartment(self) -> bool:
        """Specifies if parcel is in multi compartment

        :return: True if parcel is in multicompartment
        :rtype: bool
        """

        return self.multi_compartment is not None

    @property
    def is_main_multicompartment(self) -> bool | None:
        """Specifies if parcel is main parcel in multi compartment

        :return: True if parcel is in multicompartment
        :rtype: bool
        """

        if self.is_multicompartment and self.multi_compartment is not None:
            return self.multi_compartment.shipment_numbers is not None

        return None

    @property
    def has_airsensor(self) -> bool | None:
        if self.pickup_point is not None:
            return self.pickup_point.air_sensor_data is not None

        return None


class ReturnParcel(BaseParcel):
    # TODO: Prepare properties required to ease up access
    """Object representation of :class:`inpost.api.Inpost` returned parcel

    :param parcel_data: :class:`dict` containing all parcel data
    :type parcel_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, parcel_data: dict, logger: logging.Logger):
        """Constructor method

        :param parcel_data: dict containing parcel data
        :type parcel_data: dict
        :param logger: logger instance
        :type logger: logging.Logger
        """

        super().__init__(parcel_data, logger)
        self.uuid: str = parcel_data.get("uuid")
        self.rma: str = parcel_data.get("rma")
        self.organization_name: str = parcel_data.get("organizationName")
        self.created_date: arrow = get(parcel_data.get("createdDate"))
        self.accepted_date: arrow = get(parcel_data.get("acceptedDate"))
        self.expiry_date: arrow = get(parcel_data.get("expiryDate"))
        self.sent_date: arrow = get(parcel_data.get("sentDate"))
        self.delivered_date: arrow = get(parcel_data.get("deliveredDate"))
        self.order_number: str = parcel_data.get("orderNumber")
        self.form_type: str = parcel_data.get("formType")


class SentParcel(BaseParcel):
    # TODO: Recheck properties
    """Object representation of :class:`inpost.api.Inpost` sent parcel

    :param parcel_data: :class:`dict` containing all parcel data
    :type parcel_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, parcel_data: dict, logger: logging.Logger):
        """Constructor method

        :param parcel_data: dict containing parcel data
        :type parcel_data: dict
        :param logger: logger instance
        :type logger: logging.Logger
        """

        super().__init__(parcel_data, logger)
        self.origin_system: str | None = parcel_data.get("originSystem", None)
        self.quick_send_code: int | None = parcel_data.get("quickSendCode", None)
        self._qr_code: QRCode | None = (
            QRCode(qrcode_data=parcel_data["qrCode"], logger=self._log) if "qrCode" in parcel_data else None
        )
        self.confirmation_date: arrow = get(parcel_data.get("confirmationDate", None))
        self.shipment_type: ParcelShipmentType = ParcelShipmentType[parcel_data["shipmentType"]]
        self.parcel_size: ParcelLockerSize | ParcelCarrierSize = (
            ParcelLockerSize[parcel_data.get("parcelSize")]
            if self.shipment_type == ParcelShipmentType.parcel
            else ParcelCarrierSize[parcel_data.get("parcelSize")]
        )
        self.receiver: Receiver | None = (
            Receiver(receiver_data=parcel_data["receiver"], logger=self._log) if "receiver" in parcel_data else None
        )
        self.sender: Sender | None = (
            Sender(sender_data=parcel_data["sender"], logger=self._log) if "sender" in parcel_data else None
        )
        self.pickup_point: PickupPoint | None = (
            PickupPoint(point_data=parcel_data["pickUpPoint"], logger=self._log)
            if "pickUpPoint" in parcel_data
            else None
        )
        self.delivery_point: DeliveryPoint | None = (
            DeliveryPoint(parcel_data["deliveryPoint"], logger=self._log) if "deliveryPoint" in parcel_data else None
        )
        self.drop_off_point: DropOffPoint | None = (
            DropOffPoint(point_data=parcel_data["dropOffPoint"], logger=self._log)
            if "dropOffPoint" in parcel_data
            else None
        )
        self.payment: Payment | None = (
            Payment(payment_details=parcel_data["payment"], logger=self._log) if "payment" in parcel_data else None
        )
        self.unlabeled: bool | None = parcel_data.get("unlabeled", None)
        self.is_end_off_week_collection: bool | None = parcel_data.get("endOfWeekCollection", None)
        self.status: ParcelStatus | None = ParcelStatus[parcel_data.get("status")]
        self._compartment_properties: CompartmentProperties | None = None

    @property
    def compartment_properties(self):
        """Returns a compartment properties for :class:`SentParcel`

        :return: Compartment properties for :class:`SentParcel`
        :rtype: CompartmentProperties
        """

        self._log.debug("getting compartment properties")
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("got compartment properties")
            return self._compartment_properties

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return None

    @compartment_properties.setter
    def compartment_properties(self, compartmentproperties_data: dict):
        """Set compartment properties for :class:`SentParcel`

        :param compartmentproperties_data: :class:`dict` containing compartment properties data for :class:`SentParcel`
        :type compartmentproperties_data: dict
        """

        self._log.debug(f"setting compartment properties with {compartmentproperties_data}")
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("compartment properties set")
            self._compartment_properties = CompartmentProperties(
                compartmentproperties_data=compartmentproperties_data, logger=self._log
            )
            return

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")

    @property
    def compartment_location(self):
        """Returns a compartment location for :class:`SentParcel`

        :return: Compartment location for :class:`SentParcel`
        :rtype: CompartmentLocation
        """

        self._log.debug("getting compartment location")
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("got compartment location")
            return self._compartment_properties.location if self._compartment_properties else None

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return None

    @compartment_location.setter
    def compartment_location(self, location_data: dict):
        """Set compartment location for :class:`SentParcel`
        :param location_data: :class:`dict` containing `compartment properties` data for :class:`Parcel`
        :type location_data: dict
        """

        self._log.debug(f"setting compartment location with {location_data}")
        if self._compartment_properties is None:
            self._log.warning("tried to assign location to empty _compartment_properties")
            return

        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("compartment location set")
            self._compartment_properties.location = location_data
            return

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")

    @property
    def compartment_status(self) -> CompartmentActualStatus | None:
        """Returns a compartment status for :class:`SentParcel`

        :return: Compartment status for :class:`SentParcel`
        :rtype: CompartmentActualStatus
        """

        self._log.debug("getting compartment status")
        if self._compartment_properties is None:
            self._log.warning("tried to access empty _compartment_properties")
            return None

        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("got compartment status")
            return self._compartment_properties.status if self._compartment_properties else None

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return None

    @compartment_status.setter
    def compartment_status(self, status: str | CompartmentActualStatus):
        """Set compartment location for :class:`SentParcel`

        :param status: compartment properties status for :class:`SentParcel`
        :type status: str | CompartmentActualStatus
        """
        if self._compartment_properties is None:
            self._log.warning("tried to assign status to empty _compartment_properties")
            return

        self._log.debug(f"setting compartment status with {status}")
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("compartment status set")
            self._compartment_properties.status = status
            return

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")

    @property
    def mocked_location(self):
        """Returns a mocked location for :class:`SentParcel`

        :return: dict containing mocked location for :class:`SentParcel`
        :rtype: dict
        """

        self._log.debug("getting mocked location")
        if self.shipment_type == ParcelShipmentType.parcel:
            self._log.debug("got mocked location")
            return {
                "latitude": round(self.pickup_point.latitude + random.uniform(-0.00005, 0.00005), 6),
                "longitude": round(self.pickup_point.longitude + random.uniform(-0.00005, 0.00005), 6),
                "accuracy": round(random.uniform(1, 4), 1),
            }

        self._log.warning(f"wrong ParcelShipmentType: {repr(self.shipment_type)}")
        return None


class Receiver:
    """Object representation of :class:`BaseParcel` receiver

    :param receiver_data: :class:`dict` containing sender data for :class:`BaseParcel` and it's subclasses
    :type receiver_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, receiver_data: dict, logger: logging.Logger):
        """Constructor method

        :param receiver_data: dict containing receiver data
        :type receiver_data: dict
        :param logger: logger instance
        :type logger: logging.Logger
        """

        self.email: str | None = receiver_data.get("email")
        self.phone_number: str | None = receiver_data.get("phoneNumber")
        self.name: str | None = receiver_data.get("name")

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)

        self._log.debug("created")

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")


class Sender:
    """Object representation of :class:`BaseParcel` sender and it's subclasses

    :param sender_data: :class:`dict` containing sender data for :class:`BaseParcel` and it's subclasses
    :type sender_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, sender_data: dict, logger: logging.Logger):
        """Constructor method

        :param sender_data: dict containing sender data
        :type sender_data: dict
        :param logger: logger instance
        :type logger: logging.Logger
        """

        self.sender_name: str | None = sender_data.get("name", None)
        self.sender_email: str | None = sender_data.get("email", None)
        self._log: logging.Logger = logger.getChild(self.__class__.__name__)

        self._log.debug("created")

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")

    def __str__(self) -> str:
        return self.sender_name or ""


class Point:
    """Object representation of :class:`BaseParcel` point and it's subclasses

    :param point_data: :class:`dict` containing point data for :class:`BaseParcel` and it's subclasses
    :type point_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, point_data: dict, logger: logging.Logger):
        """Constructor method

        :param point_data: :class:`dict` containing point data for :class:`BaseParcel` and it's subclasses
        :type point_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)

        self.name: str | None = point_data.get("name")
        self.latitude: float = point_data.get("location", {}).get("latitude")
        self.longitude: float = point_data.get("location", {}).get("longitude")
        self.description: str | None = point_data.get("locationDescription")
        self.opening_hours: str | None = point_data.get("openingHours")
        self.post_code: str | None = point_data.get("addressDetails", {}).get("postCode")
        self.city: str | None = point_data.get("addressDetails", {}).get("city")
        self.province: str | None = point_data.get("addressDetails", {}).get("province")
        self.street: str | None = point_data.get("addressDetails", {}).get("street")
        self.building_number: str | None = point_data.get("addressDetails", {}).get("buildingNumber")

        self.payment_type: List[PaymentType] | None = (
            [PaymentType[pt] for pt in point_data.get("paymentType", []) if pt in PaymentType.__members__]
            if point_data.get("paymentType")
            else None
        )

        self.virtual: int | None = point_data.get("virtual")
        self.point_type: PointType | None = (
            PointType[point_data["pointType"]] if point_data.get("pointType") in PointType.__members__ else None
        )

        self.type: List[ParcelDeliveryType] | None = (
            [ParcelDeliveryType[data] for data in point_data.get("type", []) if data in ParcelDeliveryType.__members__]
            if point_data.get("type")
            else None
        )

        self.location_round_the_clock: bool = point_data.get("location247", False)
        self.doubled: bool = point_data.get("doubled", False)
        self.image_url: str | None = point_data.get("imageUrl")
        self.easy_access_zone: bool = point_data.get("easyAccessZone", False)
        self.air_sensor: bool = point_data.get("airSensor", False)
        self.air_sensor_data: AirSensorData | None = (
            AirSensorData(point_data["airSensorData"], self._log)
            if isinstance(point_data.get("airSensorData"), dict)
            else None
        )

        self.remote_send: bool | None = point_data.get("remoteSend")
        self.remote_return: bool | None = point_data.get("remoteReturn")

        self._log.debug("created")
        if self.type and ParcelDeliveryType.UNKNOWN in self.type:
            self._log.warning(f'unknown delivery type: {point_data["type"]}')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")

    def __str__(self) -> str:
        return self.name or ""

    @property
    def location(self) -> Tuple[float | None, float | None]:
        """Returns a mocked location for :class:`Point`

        :return: tuple containing location for :class:`Point`
        :rtype: tuple
        """

        self._log.debug("getting location")
        return self.latitude, self.longitude


class PickupPoint(Point):
    """Object representation of :class:`BaseParcel` and it's subclasses pick up point

    :param point_data: :class:`dict` containing pickup point data for :class:`BaseParcel` and it's subclasses
    :type point_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, point_data: dict, logger: logging.Logger):
        """Constructor method

        :param point_data: :class:`dict` containing pickup point data for :class:`BaseParcel` and it's subclasses
        :type point_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """
        super().__init__(point_data, logger)


class DropOffPoint(Point):
    """Object representation of :class:`BaseParcel` and it's subclasses drop off point

    :param point_data: :class:`dict` containing pickup point data for :class:`BaseParcel` and it's subclasses
    :type point_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, point_data: dict, logger: logging.Logger):
        """Constructor method

        :param point_data: :class:`dict` containing pickup point data for :class:`BaseParcel` and it's subclasses
        :type point_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        super().__init__(point_data, logger)


class DeliveryPoint:
    """Object representation of :class:`BaseParcel` and it's subclasses delivery point

    :param delivery_point: :class:`dict` containing delivery point data for :class:`BaseParcel` and it's subclasses delivery point
    :type delivery_point: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, delivery_point: dict, logger: logging.Logger):
        """Constructor method

        :param delivery_point: :class:`dict` containing delivery point data for :class:`BaseParcel`
        and it's subclasses delivery point
        :type delivery_point: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self.name = delivery_point.get("name")
        self.company_name = delivery_point.get("companyName")
        self.post_code = delivery_point.get("address", {}).get("postCode")
        self.city = delivery_point.get("address", {}).get("city")
        self.street = delivery_point.get("address", {}).get("street")
        self.building_number = delivery_point.get("address", {}).get("buildingNumber")
        self.flat_numer = delivery_point.get("address", {}).get("flatNumber")

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)
        self._log.debug("created")

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")


class Payment:
    """Object representation of :class:`BaseParcel` and it's subclasses payment

    :param payment_details: :class:`dict` containing payment data for :class:`BaseParcel` and it's subclasses payment
    :type payment_details: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, payment_details: dict, logger: logging.Logger):
        """Constructor method

        :param payment_details: :class:`dict` containing payment data for :class:`BaseParcel` and it's subclasses payment
        :type payment_details: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self.paid = payment_details.get("paid")
        self.total_price = payment_details.get("totalPrice")
        self.insurance_price = payment_details.get("insurancePrice")
        self.end_of_week_collection_price = payment_details.get("endOfWeekCollectionPrice")
        self.shipment_discounted = payment_details.get("shipmentDiscounted")
        self.transaction_status = payment_details.get("transactionStatus")

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)
        self._log.debug("created")

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")


class MultiCompartment:
    """Object representation of :class:`Parcel` `multicompartment`

    :param multicompartment_data: :class:`dict` containing multicompartment data for :class:`Parcel`
    :type multicompartment_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, multicompartment_data: dict, logger: logging.Logger):
        """Constructor method:param multicompartment_data: :class:`dict` containing multicompartment data for :class:`Parcel`

        :type multicompartment_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self.uuid = multicompartment_data.get("uuid")
        self.shipment_numbers: List[str] | None = multicompartment_data.get("shipmentNumbers")
        self.presentation: bool = multicompartment_data.get("presentation")
        self.collected: bool = multicompartment_data.get("collected")

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)
        self._log.debug("created")

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")


class Operations:
    """Object representation of :class:`Parcel` `operations`

    :param operations_data: :class:`dict` containing operations data for :class:`Parcel`
    :type operations_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, operations_data: dict, logger: logging.Logger):
        """Constructor method

        :param operations_data: :class:`dict` containing operations data for :class:`Parcel`
        :type operations_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self.manual_archive: bool = operations_data["manualArchive"]
        self.auto_archivable_since: arrow | None = (
            get(operations_data["autoArchivableSince"]) if "autoArchivableSince" in operations_data else None
        )
        self.delete: bool | None = operations_data.get("delete")
        self.pay_to_send: bool | None = operations_data.get("payToSend")
        self.collect: bool | None = operations_data.get("collect")
        self.expand_avizo: bool | None = operations_data.get("expandAvizo")
        self.highlight: bool | None = operations_data.get("highlight")
        self.refresh_until: arrow = get(operations_data["refreshUntil"]) if "refreshUntil" in operations_data else None
        self.request_easy_access_zone: str = operations_data.get("requestEasyAccessZone")
        self.is_voicebot: bool | None = operations_data.get("voicebot")
        self.can_share_to_observe: bool | None = operations_data.get("canShareToObserve")
        self.can_share_open_code: bool | None = operations_data.get("canShareOpenCode")
        self.can_share_parcel: bool | None = operations_data.get("canShareParcel")
        self.send: bool | None = operations_data.get("send")

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)
        self._log.debug("created")

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")


class EventLog:
    """Object representation of :class:`Parcel` single eventlog

    :param eventlog_data: :class:`dict` containing single eventlog data for :class:`Parcel`
    :type eventlog_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, eventlog_data: dict, logger: logging.Logger):
        """Constructor method

        :param eventlog_data: :class:`dict` containing single eventlog data for :class:`Parcel`
        :type eventlog_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        :raises UnknownStatusError: Unknown status in EventLog
        """

        self.type: str = eventlog_data.get("type")
        self.date: arrow = get(eventlog_data.get("date"))
        self.details: dict | None = eventlog_data.get("details")
        self._log: logging.Logger = logger.getChild(self.__class__.__name__)

        if self.type == "PARCEL_STATUS":
            self.name = ParcelStatus[eventlog_data.get("name")]
        elif self.type == "RETURN_STATUS":
            self.name = ReturnsStatus[eventlog_data.get("name")]
        elif self.type == "PAYMENT":
            self.name = PaymentStatus[eventlog_data.get("name")]
        else:
            self._log.warning(f'Unknown status type {eventlog_data.get("name")}!')
            raise UnknownStatusError(reason=eventlog_data.get("name"))

        self._log.debug("created")

        if self.name == ParcelStatus.UNKNOWN or self.name == ReturnsStatus.UNKNOWN:
            self._log.warning(f'unknown {self.type}: {eventlog_data["name"]}')

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")


class SharedTo:
    """Object representation of :class:`Parcel` single shared to

    :param sharedto_data: :class:`dict` containing shared to data for :class:`Parcel`
    :type sharedto_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, sharedto_data: dict, logger: logging.Logger):
        """Constructor method

        :param sharedto_data: :class:`dict` containing shared to data for :class:`Parcel`
        :type sharedto_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self.uuid: str = sharedto_data.get("uuid")
        self.name: str = sharedto_data.get("name")
        self.phone_number = sharedto_data.get("phoneNumber")

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)
        self._log.debug("created")

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")


class QRCode:
    """Object representation of :class:`Parcel` QRCode

    :param qrcode_data: :class:`str` containing qrcode data for :class:`Parcel`
    :type qrcode_data: str
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, qrcode_data: str, logger: logging.Logger):
        """Constructor method

        :param qrcode_data: :class:`str` containing qrcode data for :class:`Parcel`
        :type qrcode_data: str
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self._qr_code = qrcode_data

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)
        self._log.debug("created")

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")

    @property
    def qr_image(self) -> BytesIO:
        """Returns a generated QR image for :class:`QRCode`

        :return: QR Code image
        :rtype: BytesIO"""

        self._log.debug("generating qr image")
        qr = qrcode.QRCode(
            version=3, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=4, mask_pattern=5
        )

        qr.add_data(self._qr_code)
        qr.make(fit=False)
        img1 = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        bio.name = "qr.png"
        img1.save(bio, "PNG")
        bio.seek(0)
        self._log.debug("generated qr image")
        return bio


class CompartmentLocation:
    """Object representation of :class:`CompartmentProperties` compartment location

    :param compartmentlocation_data: :class:`dict` containing compartment location data for :class:`Parcel`
    :type compartmentlocation_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, compartmentlocation_data: dict, logger: logging.Logger):
        """Constructor method

        :param compartmentlocation_data: :class:`dict` containing compartment location data for :class:`Parcel`
        :type compartmentlocation_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self.name: str = compartmentlocation_data.get("compartment", {}).get("name")
        self.side: str = compartmentlocation_data.get("compartment", {}).get("location", {}).get("side")
        self.column: str = compartmentlocation_data.get("compartment", {}).get("location", {}).get("column")
        self.row: str = compartmentlocation_data.get("compartment", {}).get("location", {}).get("row")
        self.open_compartment_waiting_time: int = compartmentlocation_data.get("openCompartmentWaitingTime")
        self.action_time: int = compartmentlocation_data.get("actionTime")
        self.confirm_action_time: int = compartmentlocation_data.get("confirmActionTime")

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)
        self._log.debug("created")

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")


class CompartmentProperties:
    """Object representation of :class:`Parcel` compartment properties

    :param compartmentproperties_data: :class:`dict` containing compartment properties data for :class:`Parcel`
    :type compartmentproperties_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger"""

    def __init__(self, compartmentproperties_data: dict, logger: logging.Logger):
        """Constructor method

        :param compartmentproperties_data: :class:`dict` containing compartment properties data for :class:`Parcel`
        :type compartmentproperties_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self._session_uuid: str = compartmentproperties_data.get("sessionUuid")
        self._session_expiration_time: int = compartmentproperties_data.get("sessionExpirationTime")
        self._location: CompartmentLocation | None = None
        self._status: CompartmentActualStatus | None = None

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)
        self._log.debug("created")

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")

    @property
    def session_uuid(self):
        """Returns a session unique identified for :class:`CompartmentProperties`

        :return: string containing session unique identified for :class:`CompartmentProperties`
        :rtype: str"""

        self._log.debug("getting session uuid")
        return self._session_uuid

    @property
    def location(self):
        """Returns a compartment location for :class:`CompartmentProperties`

        :return: compartment location for :class:`CompartmentProperties`
        :rtype: str
        """

        self._log.debug("getting location")
        return self._location

    @location.setter
    def location(self, location_data: dict):
        """Set a compartment location for :class:`CompartmentProperties`

        :param location_data: dict containing compartment location data for :class:`CompartmentProperties`
        :type location_data: dict
        """

        self._log.debug("setting location")
        self._location = CompartmentLocation(location_data, self._log)

    @property
    def status(self):
        """Returns a compartment status for :class:`CompartmentProperties`

        :return: compartment location for :class:`CompartmentProperties`
        :rtype: CompartmentActualStatus
        """

        self._log.debug("getting status")
        return self._status

    @status.setter
    def status(self, status_data: str | CompartmentActualStatus):
        self._log.debug("setting status")
        self._status = (
            status_data if isinstance(status_data, CompartmentActualStatus) else CompartmentActualStatus[status_data]
        )

        if self._status == CompartmentActualStatus.UNKNOWN and isinstance(status_data, str):
            self._log.warning(f"unexpected compartment actual status: {status_data}")


class AirSensorData:
    """Object representation of :class:`Parcel` air sensor data

    :param airsensor_data: :class:`dict` containing air sensor data for :class:`Parcel`
    :type airsensor_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, airsensor_data: dict, logger: logging.Logger):
        """Constructor method

        :param airsensor_data: :class:`dict` containing air sensor data for :class:`Parcel`
        :type airsensor_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self.updated_until: arrow = airsensor_data.get("updatedUntil")
        self.air_quality: str = airsensor_data.get("airQuality")
        self.temperature: float = airsensor_data.get("temperature")
        self.humidity: float = airsensor_data.get("humidity")
        self.pressure: float = airsensor_data.get("pressure")
        self.pm25_value: float = airsensor_data.get("pollutants", {}).get("pm25", {}).get("value")
        self.pm25_percent: float = airsensor_data.get("pollutants", {}).get("pm25", {}).get("percent")
        self.pm10_value: float = airsensor_data.get("pollutants", {}).get("pm10", {}).get("value")
        self.pm10_percent: float = airsensor_data.get("pollutants", {}).get("pm10", {}).get("percent")

        self._log: logging.Logger = logger.getChild(self.__class__.__name__)
        self._log.debug("created")
