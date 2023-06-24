from arrow import Arrow, get


class Notification:  # TODO: do docs
    def __init__(self, notification_data):  # TODO: do docs
        self.id: str = notification_data.get("id", None)
        self.type: str = notification_data.get("type", None)
        self.action: str = notification_data.get("action", None)
        self.date: Arrow = get(notification_data.get("date")) if "date" in notification_data else None
        self.title: str = notification_data.get("title", None)
        self.content: str = notification_data.get("content", None)
        self.shipment_number: str = notification_data.get("shipmentNumber", None)
        self.read: bool = notification_data.get("read", None)
        self.extra_params: dict = notification_data.get("extraParams", None)
        self.parcel_type: str = notification_data.get("parcelType", None)
