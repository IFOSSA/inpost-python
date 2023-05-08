from arrow import get, Arrow


class Notification:
    def __init__(self, notification_data):
        self.id: str = notification_data['id']
        self.type: str = notification_data['type']
        self.action: str = notification_data['action']
        self.date: Arrow = get(notification_data['date'])
        self.title: str = notification_data['title']
        self.content: str = notification_data['content']
        self.shipment_number: str = notification_data['shipmentNumber']
        self.read: bool = notification_data['read']
        self.extra_params: dict = notification_data['extraParams']
        self.parcel_type: str = notification_data['parcelType']
