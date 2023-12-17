import logging

from arrow import Arrow, get


class Notification:
    """Object representation of :class:`inpost.api.Inpost` notification

    :param notification_data: :class:`dict` containing all notification data
    :type notification_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, notification_data: dict, logger: logging.Logger):
        """Constructor method

        :param notification_data: :class:`dict` containing all notification data
        :type notification_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self.id: str = notification_data.get("id", None)
        self._log: logging.Logger = logger.getChild(f"{self.__class__.__name__}.{self.id}")
        self.type: str = notification_data.get("type", None)
        self.action: str = notification_data.get("action", None)
        self.date: Arrow = get(notification_data.get("date")) if "date" in notification_data else None
        self.title: str = notification_data.get("title", None)
        self.content: str = notification_data.get("content", None)
        self.shipment_number: str = notification_data.get("shipmentNumber", None)
        self.read: bool = notification_data.get("read", None)
        self.extra_params: dict = notification_data.get("extraParams", None)
        self.parcel_type: str = notification_data.get("parcelType", None)

        self._log.debug(f"created notification with id {self.id}")
