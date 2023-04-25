import logging

from arrow import get, Arrow


class Friend:
    def __init__(self, friend_data, logger: logging.Logger):
        self.uuid: str = friend_data['uuid'] if 'uuid' in friend_data else None
        self.phone_number: str = friend_data['phoneNumber']
        self.name: str = friend_data['name']
        self._log: logging.Logger = logger.getChild(f'{__class__.__name__}.{self.uuid}')
        self.invitaion_code: str | None = friend_data['invitationCode'] if 'invitationCode' in friend_data else None
        self.created_date: Arrow | None = get(friend_data['createdDate']) if 'createdDate' in friend_data else None
        self.expiry_date: Arrow | None = get(friend_data['expiryDate']) if 'expiryDate' in friend_data else None

        if self.invitaion_code:
            self._log.debug(f'created friendship with {self.name} using from_invitation')
        else:
            self._log.debug(f'created friendship with {self.name}')

    @classmethod
    def from_invitation(cls, invitation_data, logger: logging.Logger):
        return cls(friend_data={'uuid': invitation_data['friend']['uuid'],
                                'phoneNumber': invitation_data['friend']['phoneNumber'],
                                'name': invitation_data['friend']['name'],
                                'invitationCode': invitation_data['invitationCode'],
                                'createdDate': invitation_data['createdDate'],
                                'expiryDate': invitation_data['expiryDate']
                                },
                   logger=logger)

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != '_log')
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("\'", "")
