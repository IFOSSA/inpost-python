import logging

from arrow import Arrow, get


class Friend:
    """Object representation of :class:`inpost.api.Inpost` friend

    :param friend_data: :class:`dict` containing all friend data
    :type friend_data: dict
    :param logger: :class:`logging.Logger` parent instance
    :type logger: logging.Logger
    """

    def __init__(self, friend_data: dict, logger: logging.Logger):
        """Constructor method

        :param friend_data: :class:`dict` containing all friend data
        :type friend_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        """

        self.uuid: str = friend_data["uuid"] if "uuid" in friend_data else None
        self.phone_number: str = friend_data["phoneNumber"]
        self.name: str = friend_data["name"]
        self._log: logging.Logger = logger.getChild(f"{self.__class__.__name__}.{self.uuid}")
        self.invitaion_code: str | None = friend_data["invitationCode"] if "invitationCode" in friend_data else None
        self.created_date: Arrow | None = get(friend_data["createdDate"]) if "createdDate" in friend_data else None
        self.expiry_date: Arrow | None = get(friend_data["expiryDate"]) if "expiryDate" in friend_data else None

        if self.invitaion_code:
            self._log.debug(f"created friendship with {self.name} using from_invitation")
        else:
            self._log.debug(f"created friendship with {self.name}")

    @classmethod
    def from_invitation(cls, invitation_data: dict, logger: logging.Logger):
        """`Classmethod` to initialize :class:`Friend` from incitation.
        Should be used when retrieving configuration from database.

        :param invitation_data: :class:`dict` containing all friend data
        :type invitation_data: dict
        :param logger: :class:`logging.Logger` parent instance
        :type logger: logging.Logger
        :return: Friend object from provided invitation
        :rtype: Friend
        """

        return cls(
            friend_data={
                "uuid": invitation_data["friend"]["uuid"],
                "phoneNumber": invitation_data["friend"]["phoneNumber"],
                "name": invitation_data["friend"]["name"],
                "invitationCode": invitation_data["invitationCode"],
                "createdDate": invitation_data["createdDate"],
                "expiryDate": invitation_data["expiryDate"],
            },
            logger=logger,
        )

    def __repr__(self):
        fields = tuple(f"{k}={v}" for k, v in self.__dict__.items() if k != "_log")
        return self.__class__.__name__ + str(tuple(sorted(fields))).replace("'", "")
