import logging
from typing import List

from aiohttp import ClientResponse, ClientSession
from aiohttp.typedefs import StrOrURL

from inpost.static import (
    CompartmentExpectedStatus,
    DeliveryType,
    Friend,
    MissingParamsError,
    NoParcelError,
    NotAuthenticatedError,
    NotFoundError,
    Parcel,
    ParcelCarrierSize,
    ParcelLockerSize,
    ParcelPointOperations,
    ParcelShipmentType,
    ParcelStatus,
    ParcelType,
    ParcelTypeError,
    PhoneNumberError,
    Point,
    ReAuthenticationError,
    Receiver,
    RefreshTokenError,
    ReturnParcel,
    Sender,
    SentParcel,
    SingleParamError,
    SmsCodeError,
    UnauthorizedError,
    UnidentifiedAPIError,
    appjson,
    blik_status_url,
    collect_url,
    compartment_open_url,
    compartment_status_url,
    confirm_sms_code_url,
    create_blik_url,
    create_url,
    friendship_url,
    logout_url,
    multi_url,
    open_sent_url,
    parcel_points_url,
    parcel_prices_url,
    refresh_token_url,
    returns_url,
    send_sms_code_url,
    sent_url,
    shared_url,
    status_sent_url,
    terminate_collect_session_url,
    tracked_url,
    validate_friendship_url,
    validate_sent_url,
)


class Inpost:
    """Python representation of an Inpost app. Essentially implements methods to manage all incoming parcels"""

    def __init__(self, phone_number):
        """Constructor method

        :param phone_number: phone number
        :type phone_number: str
        :raises PhoneNumberError: Wrong phone number format or is not digit
        """

        if isinstance(phone_number, int):
            phone_number = str(phone_number)

        if not (len(phone_number) == 9 and phone_number.isdigit()):
            raise PhoneNumberError(f"Wrong phone number format: {phone_number} (should be 9 digits)")

        self.phone_number: str = phone_number
        self.sms_code: str | None = None
        self.auth_token: str | None = None
        self.refr_token: str | None = None
        self.sess: ClientSession = ClientSession()
        self._log = logging.getLogger(f"{self.__class__.__name__}.{phone_number}")

        self._log.setLevel(level=logging.DEBUG)
        self._log.info(f"initialized inpost object with phone number {phone_number}")

    def __repr__(self):
        return f"{self.__class__.__name__}(phone_number={self.phone_number})"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.disconnect()

    async def request(
        self,
        method: str,
        action: str,
        url: StrOrURL,
        auth: bool = True,
        headers: dict | None = None,
        params: dict | None = None,
        data: dict | None = None,
        autorefresh: bool = True,
        **kwargs,
    ) -> ClientResponse:
        """Validates sent data and fetches required compartment properties for opening

        :param method: HTTP method of request
        :type method: str
        :param action: action type (e.g. "get parcels" or "send sms code") for logging purposes
        :type action: str
        :param url: HTTP request url
        :type url: StrOrURL
        :param auth: True if request should contain authorization header else False
        :type auth: bool
        :param headers: Additional headers for HTTP request (don't put authorization header here)
        :type headers: dict | None
        :param params: dict of parameters to get method
        :type params: dict | None
        :param data: Data to be sent in HTTP request
        :type data: dict | None
        :param autorefresh: method automatically try to refresh token if API returns HTTP 401 Unauthorized status code
        :type autorefresh: bool
        :param kwargs: additional keyword arguments
        :return: response of http request
        :rtype: ClientResponse
        :raises UnauthorizedError: User not authenticated in inpost service
        :raises NotFoundError: URL not found
        :raises UnidentifiedAPIError: Unexpected things happened
        :raises ValueError: Doubled authorization header in request
        """

        if auth and headers:
            if "Authorization" in headers:
                raise ValueError("Both auth==True and Authorization in additional headers")

        headers_ = {} if headers is None else headers

        if auth:
            headers_.update({"Authorization": self.auth_token})

        resp = await self.sess.request(method, url, headers=headers_, params=params, json=data, **kwargs)

        if autorefresh and resp.status == 401:
            await self.refresh_token()
            headers_.update({"Authorization": self.auth_token})
            resp = await self.sess.request(method, url, headers=headers_, params=params, json=data, **kwargs)

        match resp.status:
            case 200:
                self._log.debug(f"{action} done")
                return resp
            case 401:
                self._log.error(f"could not perform {action}, unauthorized")
                raise UnauthorizedError(reason=resp)
            case 404:
                self._log.error(f"could not perform {action}, not found")
                raise NotFoundError(reason=resp)
            case _:
                self._log.error(f"could not perform {action}, unhandled status")

        raise UnidentifiedAPIError(reason=resp)

    @classmethod
    def from_dict(cls, data: dict) -> "Inpost":
        """`Classmethod` to initialize :class:`Inpost` object with dict.
        Should be used when retrieving configuration from database.

        :param data: User's Inpost data (e.g. phone_number, sms_code, auth_token, refr_token)
        :type data: dict
        :return: Inpost object from provided dict
        :rtype: Inpost
        """

        inp = cls(phone_number=data["phone_number"])
        inp.sms_code = data["sms_code"]
        inp.auth_token = data["auth_token"]
        inp.refr_token = data["refr_token"]

        inp._log.info("initialized by from_dict")
        return inp

    async def send_sms_code(self) -> bool:
        """Sends sms code to `Inpost.phone_number`

        :return: True if sms code is sent else False
        :rtype: bool
        :raises PhoneNumberError: Missing phone number
        """

        if not self.phone_number:  # can't log it cuz if there's no phone number no logger initialized @shrug
            raise PhoneNumberError("Phone number missing")

        self._log.info("sending sms code")

        resp = await self.request(
            method="post",
            action="send sms code",
            url=send_sms_code_url,
            auth=False,
            headers=None,
            data={"phoneNumber": f"{self.phone_number}"},
            autorefresh=False,
        )

        return resp.status == 200

    async def confirm_sms_code(self, sms_code: str | int) -> bool:
        """Confirms sms code sent to `Inpost.phone_number` and fetches tokens

        :param sms_code: sms code sent to Inpost.phone_number device
        :type sms_code: str | int
        :return: True if sms code gets confirmed and tokens fetched
        :rtype: bool
        :raises PhoneNumberError: Missing phone number
        :raises SmsCodeError: Wrong sms code format
        """

        if not self.phone_number:  # can't log it cuz if there's no phone number no logger initialized @shrug
            raise PhoneNumberError("Phone number missing")

        if isinstance(sms_code, int):
            sms_code = str(sms_code)

        if len(sms_code) != 6 or not sms_code.isdigit():
            raise SmsCodeError(reason=f"Wrong sms code format: {sms_code} (should be 6 digits)")

        self._log.info("confirming sms code")

        resp = await self.request(
            method="post",
            action="confirm sms code",
            url=confirm_sms_code_url,
            auth=False,
            headers=appjson,
            data={"phoneNumber": self.phone_number, "smsCode": sms_code, "phoneOS": "Android"},
            autorefresh=False,
        )

        if resp.status == 200:
            auth_token_data = await resp.json()
            self.sms_code = sms_code
            self.refr_token = auth_token_data["refreshToken"]
            self.auth_token = auth_token_data["authToken"]
            self._log.debug("sms code confirmed")
            return True

        return False

    async def refresh_token(self) -> bool:
        """Refreshes authorization token using refresh token

        :return: True if Inpost.auth_token gets refreshed
        :rtype: bool
        :raises RefreshTokenError: Missing refresh token
        :raises ReAuthenticationError: Re-authentication needed
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info("refreshing token")

        if not self.refr_token:
            self._log.error("refresh token missing")
            raise RefreshTokenError(reason="Refresh token missing")

        resp = await self.request(
            method="post",
            action="refresh token",
            url=refresh_token_url,
            auth=False,
            headers=appjson,
            data={"refreshToken": self.refr_token, "phoneOS": "Android"},
            autorefresh=False,
        )

        if resp.status == 200:
            confirmation = await resp.json()
            if confirmation["reauthenticationRequired"]:
                self._log.error("could not refresh token, log in again")
                raise ReAuthenticationError(reason="You need to log in again!")

            self.auth_token = confirmation["authToken"]
            self._log.debug("token refreshed")
            return True

        return False

    async def logout(self) -> bool:
        """Logouts user from inpost api service

        :return: True if the user is logged out
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info("logging out")

        if not self.auth_token:
            self._log.error("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="post", action="logout", url=logout_url, auth=True, headers=None, data=None, autorefresh=True
        )

        if resp.status == 200:
            self.phone_number = ""
            self.refr_token = None
            self.auth_token = None
            self.sms_code = None
            self._log.debug("logged out")
            return True

        return False

    async def disconnect(self) -> bool:
        """Simplified method to logout and close user's session

        :return: True if user is logged out and session is closed else False
        :raises NotAuthenticatedError: User not authenticated in inpost service
        """

        self._log.info("disconnecting")
        if not self.auth_token:
            self._log.error("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        if await self.logout():
            await self.sess.close()
            self._log.debug("disconnected")
            return True

        self._log.error("could not disconnect")
        return False

    async def get_parcel(
        self, shipment_number: int | str, parcel_type: ParcelType = ParcelType.TRACKED, parse=False
    ) -> dict | Parcel | SentParcel | ReturnParcel:
        """Fetches single parcel from provided shipment number

        :param shipment_number: Parcel's shipment number
        :type shipment_number: int | str
        :param parcel_type: Parcel type (e.g. received, sent, returned)
        :type parcel_type: ParcelType
        :param parse: if set to True method will return :class:`Parcel` else :class:`dict`
        :type parse: bool
        :return: Fetched parcel data
        :rtype: dict | Parcel
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        :raises ParcelTypeError: Unknown parcel type selected
        """

        self._log.info(f"getting parcel with shipment number: {shipment_number}")

        if not self.auth_token:
            self._log.error("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        match parcel_type:
            case ParcelType.TRACKED:
                self._log.debug(f"getting parcel type {parcel_type}")
                url = tracked_url
            case ParcelType.SENT:
                self._log.debug(f"getting parcel type {parcel_type}")
                url = sent_url
            case ParcelType.RETURNS:
                self._log.debug(f"getting parcel type {parcel_type}")
                url = returns_url
            case _:
                self._log.error(f"unexpected parcel type {parcel_type}")
                raise ParcelTypeError(reason=f"Unexpected parcel type: {parcel_type}")

        resp = await self.request(
            method="get",
            action=f"parcel with shipment number {shipment_number}",
            url=f"{url}{shipment_number}",
            auth=True,
            headers=None,
            data=None,
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"parcel with shipment number {shipment_number} received")
            match parcel_type:
                case ParcelType.TRACKED:
                    return await resp.json() if not parse else Parcel(await resp.json(), logger=self._log)
                case ParcelType.SENT:
                    return await resp.json() if not parse else SentParcel(await resp.json(), logger=self._log)
                case ParcelType.RETURNS:
                    return await resp.json() if not parse else ReturnParcel(await resp.json(), logger=self._log)
                case _:
                    self._log.error(f"wrong parcel type {parcel_type}")
                    raise ParcelTypeError(reason=f"Unknown parcel type: {parcel_type}")

        raise UnidentifiedAPIError(reason=resp)

    async def get_parcels(
        self,
        parcel_type: ParcelType = ParcelType.TRACKED,
        status: ParcelStatus | List[ParcelStatus] | None = None,
        pickup_point: str | List[str] | None = None,
        shipment_type: ParcelShipmentType | List[ParcelShipmentType] | None = None,
        parse: bool = False,
    ) -> List[dict] | List[Parcel]:
        """Fetches all available parcels for set `Inpost.phone_number` and optionally filters them

        :param parcel_type: Parcel type (e.g. received, sent, returned)
        :type parcel_type: ParcelType
        :param status: status that each fetched parcels has to be in
        :type status: ParcelStatus | list[ParcelStatus] | None
        :param pickup_point: Fetched parcels have to be picked from this pickup point (e.g. `GXO05M`)
        :type pickup_point: str | list[str] | None
        :param shipment_type: Fetched parcels have to be shipped that way
        :type shipment_type: ParcelShipmentType | list[ParcelShipmentType] | None
        :param parse: if set to True method will return list[:class:`Parcel`] else list[:class:`dict`]
        :type parse: bool
        :return: fetched parcels data
        :rtype: list[dict] | list[Parcel]
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises ParcelTypeError: Unknown parcel type selected
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info("getting parcels")

        if not self.auth_token:
            self._log.error("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        match parcel_type:
            case ParcelType.TRACKED:
                self._log.debug(f"getting parcel type {parcel_type}")
                url = tracked_url
            case ParcelType.SENT:
                self._log.debug(f"getting parcel type {parcel_type}")
                url = sent_url
            case ParcelType.RETURNS:
                self._log.debug(f"getting parcel type {parcel_type}")
                url = returns_url
            case _:
                self._log.error(f"wrong parcel type {parcel_type}")
                raise ParcelTypeError(reason=f"Unknown parcel type: {parcel_type}")

        async with await self.request(
            method="get", action="get parcels", url=url, auth=True, headers=None, data=None, autorefresh=True
        ) as resp:
            if resp.status != 200:
                self._log.debug(f"Could not get parcels due to HTTP error {resp.status}")
                raise UnidentifiedAPIError(reason=resp)

            self._log.debug(f"received {parcel_type} parcels")
            _parcels = (await resp.json())["parcels"]

            if status is not None:
                if isinstance(status, ParcelStatus):
                    status = [status]

                _parcels = (_parcel for _parcel in _parcels if ParcelStatus[_parcel.get("status")] in status)

            if pickup_point is not None:
                if isinstance(pickup_point, str):
                    pickup_point = [pickup_point]

                _parcels = (_parcel for _parcel in _parcels if _parcel["pickUpPoint"]["name"] in pickup_point)

            if shipment_type is not None:
                if isinstance(shipment_type, ParcelShipmentType):
                    shipment_type = [shipment_type]

                _parcels = (
                    _parcel
                    for _parcel in _parcels
                    if ParcelShipmentType[_parcel["shipmentType"]] in list(shipment_type)
                )

            return list(_parcels) if not parse else [Parcel(parcel_data=data, logger=self._log) for data in _parcels]

    async def get_multi_compartment(self, multi_uuid: str | int, parse: bool = False) -> dict | List[Parcel]:
        """Fetches all available parcels for set `Inpost.phone_number` and optionally filters them

        :param multi_uuid: multicompartment uuid
        :type multi_uuid: str | int
        :param parse: switch for parsing response
        :type parse: bool
        :return: multicompartment parcels
        :rtype: dict | List[Parcel]
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        if not self.auth_token:
            self._log.error("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="get",
            action=f"parcel with multi-compartment uuid {multi_uuid}",
            url=f"{multi_url}{multi_uuid}",
            auth=True,
            headers=None,
            data=None,
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"parcel with multi-compartment uuid {multi_uuid} received")
            return (
                (await resp.json())["parcels"]
                if not parse
                else [Parcel(data, logger=self._log) for data in (await resp.json())["parcels"]]
            )

        raise UnidentifiedAPIError(reason=resp)

    async def collect_compartment_properties(
        self, shipment_number: str | int | None = None, parcel_obj: Parcel | None = None, location: dict | None = None
    ) -> Parcel:
        """Validates sent data and fetches required compartment properties for opening

        :param shipment_number: Parcel's shipment number
        :type shipment_number: int | str | None
        :param parcel_obj: :class:`Parcel` object to obtain data from
        :type parcel_obj: Parcel | None
        :param location: Fetched parcels have to be picked from this pickup point (e.g. `GXO05M`)
        :type location: dict | None
        :return: fetched parcels data
        :rtype: Parcel
        :raises MissingParamsError: none of required query and location params are filled
        :raises SingleParamError: Fields shipment_number and parcel_obj filled in but only one of them is required
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises NoParcelError: Could not get parcel object from provided data
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened

        .. warning:: you must fill in only one parameter - shipment_number or parcel_obj!
        """

        parcel_obj_: Parcel | None = None
        if shipment_number is None is parcel_obj:
            self._log.error("none of shipment_number and parcel_obj filled in")
            raise MissingParamsError(reason="None of params are filled (one required)")
        elif shipment_number is not None is not parcel_obj:
            self._log.error("shipment_number and parcel_obj filled in")
            raise SingleParamError(reason="Fields shipment_number and parcel_obj filled in! Choose one!")
        elif shipment_number:
            self._log.debug(f"parcel_obj not provided, getting from shipment number {shipment_number}")
            parcel_obj_ = await self.get_parcel(shipment_number=shipment_number, parse=True)
        elif parcel_obj:
            parcel_obj_ = parcel_obj

        if parcel_obj_ is None:
            raise NoParcelError(reason="Could not obtain desired parcel!")

        self._log.info(f"collecting compartment properties for {parcel_obj_.shipment_number}")

        resp = await self.request(
            method="post",
            action="collect compartment properties",
            url=collect_url,
            auth=True,
            headers=None,
            data={
                "parcel": parcel_obj_.compartment_open_data,
                "geoPoint": location if location is not None else parcel_obj_.mocked_location,
            },
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"collected compartment properties for {parcel_obj_.shipment_number}")
            parcel_obj_.compartment_properties = await resp.json()
            return parcel_obj_

        raise UnidentifiedAPIError(reason=resp)

    async def open_compartment(self, parcel_obj: Parcel) -> Parcel:
        """Opens compartment for `Inpost.parcel` object

        :param parcel_obj: Parcel object
        :type parcel_obj: Parcel
        :return: Parcel with compartment location set if it gets opened
        :rtype: Parcel
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info(f"opening compartment for {parcel_obj.shipment_number}")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="post",
            action=f"open compartment for {parcel_obj.shipment_number}",
            url=compartment_open_url,
            auth=True,
            headers=None,
            data={"sessionUuid": parcel_obj.compartment_properties.session_uuid},
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"opened compartment for {parcel_obj.shipment_number}")
            parcel_obj.compartment_location = await resp.json()
            return parcel_obj

        raise UnidentifiedAPIError(reason=resp)

    async def check_compartment_status(
        self, parcel_obj: Parcel, expected_status: CompartmentExpectedStatus = CompartmentExpectedStatus.OPENED
    ) -> bool:
        """Checks and compare compartment status (e.g. opened, closed) with expected status

        :param parcel_obj: Parcel object
        :type parcel_obj: Parcel
        :param expected_status: Compartment expected status
        :type expected_status: CompartmentExpectedStatus
        :return: True if actual status equals expected status else False
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info(f"checking compartment status for {parcel_obj.shipment_number}")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="post",
            action="check compartment status",
            url=compartment_status_url,
            auth=True,
            headers=None,
            data={
                "sessionUuid": parcel_obj.compartment_properties.session_uuid,
                "expectedStatus": expected_status.name,
            },
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"checked compartment status for {parcel_obj.shipment_number}")
            parcel_obj.compartment_status = (await resp.json())["status"]
            return CompartmentExpectedStatus[(await resp.json())["status"]] == expected_status

        raise UnidentifiedAPIError(reason=resp)

    async def terminate_collect_session(self, parcel_obj: Parcel) -> bool:
        """Terminates user session in inpost api service

        :param parcel_obj: Parcel object
        :type parcel_obj: Parcel
        :return: True if the user session is terminated
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info(f"terminating collect session for {parcel_obj.shipment_number}")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="post",
            action="terminate collect session",
            url=terminate_collect_session_url,
            auth=True,
            headers=None,
            data={"sessionUuid": parcel_obj.compartment_properties.session_uuid},
            autorefresh=True,
        )
        if resp.status == 200:
            self._log.debug(f"terminated collect session for {parcel_obj.shipment_number}")
            return True

        raise UnidentifiedAPIError(reason=resp)

    async def collect(
        self, shipment_number: str | None = None, parcel_obj: Parcel | None = None, location: dict | None = None
    ) -> Parcel | None:
        """Simplified method to open compartment

        :param shipment_number: Parcel's shipment number
        :type shipment_number: int | str | None
        :param parcel_obj: :class:`Parcel` object to obtain data from
        :type parcel_obj: Parcel | None
        :param location: Fetched parcels have to be picked from this pickup point (e.g. `GXO05M`)
        :type location: dict | None
        :return: fetched parcels data
        :rtype: bool
        :raises SingleParamError: Fields shipment_number and parcel_obj filled in but only one of them is required
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises NoParcelError: Could not get parcel object from provided data
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened

        .. warning:: you must fill in only one parameter - shipment_number or parcel_obj!
        """

        if shipment_number and parcel_obj:
            self._log.error("shipment_number and parcel_obj filled in")
            raise SingleParamError(reason="Fields shipment_number and parcel_obj filled! Choose one!")

        if not self.auth_token:
            self._log.error("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        if shipment_number is not None and parcel_obj is None:
            parcel_obj = await self.get_parcel(shipment_number=shipment_number, parse=True)

        if parcel_obj is None:
            raise NoParcelError(reason="Could not obtain desired parcel!")

        self._log.info(f"collecting parcel with shipment number {parcel_obj.shipment_number}")

        if parcel_obj_ := await self.collect_compartment_properties(parcel_obj=parcel_obj, location=location):
            if parcel_obj__ := await self.open_compartment(parcel_obj=parcel_obj_):
                if await self.check_compartment_status(parcel_obj=parcel_obj__):
                    return parcel_obj__

        return None

    async def close_compartment(self, parcel_obj: Parcel) -> bool:
        """Checks whether actual compartment status and expected one matches then notifies inpost api that
        compartment is closed. Should be invoked after collecting parcel

        :param parcel_obj: Parcel object
        :type parcel_obj: Parcel
        :return: True if compartment status is closed and successfully terminates user's session else False
        :rtype: bool
        """

        self._log.info(f"closing compartment for {parcel_obj.shipment_number}")

        if await self.check_compartment_status(expected_status=CompartmentExpectedStatus.CLOSED, parcel_obj=parcel_obj):
            if await self.terminate_collect_session(parcel_obj=parcel_obj):
                return True

        return False

    async def reopen_compartment(self, parcel_obj: Parcel) -> bool:
        """Reopens compartment for `Inpost.parcel` object

        :param parcel_obj: Parcel object
        :type parcel_obj: Parcel
        :return: True if compartment gets reopened
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info(f"reopening compartment for {parcel_obj.shipment_number}")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="post",
            action=f"reopen compartment for {parcel_obj.shipment_number}",
            url=compartment_open_url,
            auth=True,
            headers=None,
            data={"sessionUuid": parcel_obj.compartment_properties.session_uuid},
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"opened compartment for {parcel_obj.shipment_number}")
            return True

        raise UnidentifiedAPIError(reason=resp)

    async def get_parcel_points(
        self,
        query: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        per_page: int = 1000,
        operation: ParcelPointOperations = ParcelPointOperations.CREATE,
        parse: bool = True,
    ) -> dict | List[Point]:
        """Fetches parcel points for inpost services

        :param query: parcel point search query (e.g. GXO05M)
        :type query: str | None
        :param latitude: latitude of place we are looking for nearby parcel points
        :type latitude: float | None
        :param longitude: longitude of place we are looking for nearby parcel points
        :type longitude: float | None
        :param per_page: number of parcel points we would like to get from query, defaults to 1000
        :type per_page: int
        :param operation: operation you want to perform (e.g. CREATE, SEND)
        :type operation: ParcelPointOperations
        :param parse: parse output or not, defaults to True
        :type parse: bool
        :return: :class:`dict` of prices for inpost services
        :rtype: dict
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises SingleParamError: query and location params filled, but only one is required
        :raises MissingParamsError: none of required query and location params are filled
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info("getting parcel prices")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        if query is not None and (latitude is not None and longitude is not None):
            self._log.debug("query and location provided")
            raise SingleParamError(reason="Fields query and location filled! Chose one!")

        _params = {"filter": operation.value, "perPage": per_page}

        if query is not None:
            _params.update({"query": query})
        elif latitude is not None and longitude is not None:
            _params.update({"relative_point": f"{latitude},{longitude}"})
        else:
            raise MissingParamsError(reason="None of params are filled (one required)")

        resp = await self.request(
            method="get",
            action="get parcel points",
            url=parcel_points_url,
            auth=True,
            headers=None,
            params=_params,
            data=None,
            autorefresh=True,
        )
        if resp.status == 200:
            self._log.debug("got parcel prices")
            return (
                await resp.json()
                if not parse
                else [Point(point_data=point, logger=self._log) for point in (await resp.json())["points"]]
            )

        raise UnidentifiedAPIError(reason=resp)

    async def blik_status(self) -> bool:
        """Checks if user has active blik session


        :return: True if user has no active blik sessions else False
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        """

        if not self.auth_token:
            self._log.error("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        self._log.info("checking if user has opened blik session")

        resp = await self.request(
            method="get",
            action="check user blik session",
            url=blik_status_url,
            auth=True,
            headers=None,
            autorefresh=True,
        )

        if resp.status == 200 and not (await resp.json())["active"]:
            self._log.debug("user has no active blik sessions")
            return True

        return False

    async def create_parcel(
        self,
        delivery_type: DeliveryType,
        parcel_size: ParcelLockerSize | ParcelCarrierSize,
        price: float | str,
        sender: Sender,
        receiver: Receiver,
        delivery_point: Point,
    ) -> dict | None:
        """Fetches parcel points for inpost services

        :param delivery_type: a way parcel will be delivered
        :type delivery_type: DeliveryType
        :param parcel_size: size of parcel
        :type parcel_size: ParcelLockerSize | ParcelCarrierSize
        :param price: price for chosen parcel size
        :type price: float | str
        :param sender: parcel sender
        :type sender: Sender
        :param receiver: parcel receiver
        :type receiver: Receiver
        :param delivery_point: parcel delivery point
        :type delivery_point: Point
        :return: :class:`dict` with response
        :rtype: dict | None
        :raises UnidentifiedAPIError: Unexpected thing happened
        :raises NotAuthenticatedError: User not authenticated in inpost service
        """

        if not self.auth_token:
            self._log.error("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        self._log.info("creating new parcel")

        resp = await self.request(
            method="post",
            action="create parcel",
            url=create_url,
            auth=True,
            headers=None,
            data={
                "deliveryType": delivery_type.value,
                "parcelSize": parcel_size.name,
                "price": price,
                "sender": {"name": sender.sender_name, "email": sender.sender_email},
                "receiver": {"name": receiver.name, "email": receiver.email, "phoneNumber": receiver.phone_number},
                "deliveryPoint": {"boxMachineName": delivery_point.name},
            },
            autorefresh=True,
        )

        if resp.status == 200:
            return await resp.json()

        raise UnidentifiedAPIError(reason=resp)

    async def create_blik_session(
        self, amount: float | str, shipment_number: str, currency: str = "PLN"
    ) -> None | dict:
        """Creates blik session for sending parcel

        :param amount: amount of money that has to be paid
        :type amount: float | str
        :param shipment_number: shipment number of parcel that is being sent
        :type shipment_number: str
        :param currency: currency of `amount`
        :type currency: str
        :return: True if user has no active blik sessions else False
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        if not self.auth_token:
            self._log.error("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        self._log.info(f"creating blik session for {shipment_number}")

        resp = await self.request(
            method="post",
            action="create blik session",
            url=create_blik_url,
            auth=True,
            headers=None,
            data={
                "shipmentNumber": shipment_number,
                "amount": amount,
                "currency": currency,
                "process": "C2X",
                "paymentMethod": "CODE",
            },
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"created blik session for {shipment_number}")
            return await resp.json()

        raise UnidentifiedAPIError(reason=resp)

    async def validate_send(
        self,
        drop_off_point: str,
        shipment_number: str | None = None,
        parcel_obj: SentParcel | None = None,
        location: dict | None = None,
    ) -> SentParcel:
        """Validates sending parcel

        :param drop_off_point: parcel machine codename where you want to drop-opp parcel
        :type drop_off_point: str
        :param shipment_number: sent parcel shipment number
        :type shipment_number: str | None
        :param parcel_obj: sent parcel object
        :type parcel_obj: SentParcel | None
        :param location: ...
        :type location: dict | None
        :return: Sent parcel with filled compartment properties
        :rtype: SentParcel
        :raises SingleParamError: Fields shipment_number and parcel_obj filled in but only one of them is required
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises NoParcelError: Could not get parcel object from provided data
        :raises MissingParamsError: None of required shipment number and parcel object params are filled
        :raises ValueError: Missing drop-off point
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        if not self.auth_token:
            self._log.error("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        parcel_obj_: SentParcel | None = None
        if shipment_number is None is parcel_obj:
            self._log.error("none of shipment_number and parcel_obj filled in")
            raise MissingParamsError(reason="None of params are filled (one required)")
        elif shipment_number is not None is not parcel_obj:
            self._log.error("shipment_number and parcel_obj filled in")
            raise SingleParamError(reason="Fields shipment_number and parcel_obj filled in! Choose one!")
        elif shipment_number:
            self._log.debug(f"parcel_obj not provided, getting from shipment number {shipment_number}")
            parcel_obj_ = await self.get_parcel(
                shipment_number=shipment_number, parcel_type=ParcelType.SENT, parse=True
            )
        elif parcel_obj:
            parcel_obj_ = parcel_obj

        if parcel_obj_ is None:
            raise NoParcelError(reason="Could not obtain parcel!")

        if parcel_obj_.drop_off_point is None:
            raise ValueError("Missing drop-off point!")

        self._log.info(f"validating send for {parcel_obj_.shipment_number}")

        resp = await self.request(
            method="post",
            action="validate send parcel data",
            url=validate_sent_url,
            auth=True,
            headers=None,
            data={
                "parcel": {
                    "shipmentNumber": parcel_obj_.shipment_number,
                    "quickSendCode": parcel_obj_.quick_send_code,
                },
                "geoPoint": location,
                "boxMachineName": drop_off_point,
            },
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"validated send for for {parcel_obj_.shipment_number}")
            parcel_obj_.compartment_properties = await resp.json()
            return parcel_obj_

        raise UnidentifiedAPIError(reason=resp)

    async def open_send_compartment(self, parcel_obj: Parcel) -> bool:
        """Opens compartment on parcel that is being sent

        :param parcel_obj: Parcel object
        :type parcel_obj: Parcel
        :return: True if successfully opened compartment else False
        :rtype: bool
        :raises NotAuthenticatedError: User not logged in (missing auth_token)
        """

        self._log.info(f"opening compartment for {parcel_obj.shipment_number}")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="post",
            action=f"open send compartment for {parcel_obj.shipment_number}",
            url=open_sent_url,
            auth=True,
            headers=None,
            data={"sessionUuid": parcel_obj.compartment_properties.session_uuid},
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"opened send compartment for {parcel_obj.shipment_number}")
            return True

        return False

    async def reopen_send_compartment(self, parcel_obj: SentParcel) -> bool:
        """Reopens compartment after sending process

        :param parcel_obj: Parcel object
        :type parcel_obj: SentParcel
        :return: True if successfully reopened compartment else False
        :rtype: bool
        :raises NotAuthenticatedError: User not logged in (missing auth_token)
        """

        self._log.info(f"reopening send compartment for {parcel_obj.shipment_number}")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="post",
            action=f"reopen compartment for {parcel_obj.shipment_number}",
            url=compartment_open_url,
            auth=True,
            headers=None,
            data={"sessionUuid": parcel_obj.compartment_properties.session_uuid},
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"opened send compartment for {parcel_obj.shipment_number}")
            return True

        return False

    async def check_send_compartment_status(
        self, parcel_obj: SentParcel, expected_status: CompartmentExpectedStatus = CompartmentExpectedStatus.OPENED
    ) -> bool:
        """Checks and compare compartment status (e.g. opened, closed) with expected status

        :param parcel_obj: Parcel object
        :type parcel_obj: SentParcel
        :param expected_status: Compartment expected status
        :type expected_status: CompartmentExpectedStatus
        :return: True if actual status equals expected status else False
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info(f"checking compartment status for {parcel_obj.shipment_number}")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="post",
            action="check send compartment status",
            url=status_sent_url,
            auth=True,
            headers=None,
            data={
                "sessionUuid": parcel_obj.compartment_properties.session_uuid,
                "expectedStatus": expected_status.name,
            },
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug(f"checked send compartment status for {parcel_obj.shipment_number}")
            parcel_obj.compartment_status = (await resp.json())["status"]
            return CompartmentExpectedStatus[(await resp.json())["status"]] == expected_status

        return False

    async def get_prices(self) -> dict:
        """Fetches prices for inpost services

        :return: :class:`dict` of prices for inpost services
        :rtype: dict
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info("getting parcel prices")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="get",
            action="get prices",
            url=parcel_prices_url,
            auth=True,
            headers=None,
            data=None,
            autorefresh=True,
        )
        if resp.status == 200:
            self._log.debug("got parcel prices")
            return await resp.json()

        raise UnidentifiedAPIError(reason=resp)

    async def get_friends(self, parse=False) -> dict | List[Friend]:
        """Fetches user friends for inpost services

        :param parse: switch for parsing response
        :type parse: bool
        :return: :class:`dict` of user friends for inpost services
        :rtype: dict
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info("getting friends")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="get", action="get friends", url=friendship_url, auth=True, headers=None, data=None, autorefresh=True
        )
        if resp.status == 200:
            self._log.debug("got user friends")
            _friends = await resp.json()
            return (
                _friends
                if not parse
                else [Friend(friend_data=friend, logger=self._log) for friend in _friends["friends"]]
            )

        raise UnidentifiedAPIError(reason=resp)

    async def get_parcel_friends(self, shipment_number: int | str, parse=False) -> dict:
        """Fetches parcel friends

        :param shipment_number: shipment number of parcel that friends are fetched
        :type shipment_number: int | str
        :param parse: switch for parsing response
        :type parse: bool
        :return: dict containing friends data
        :rtype: dict
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info("getting parcel friends")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="get",
            action="get parcel friends",
            url=f"{friendship_url}{shipment_number}",
            auth=True,
            headers=None,
            data=None,
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug("got parcel friends")
            r = await resp.json()
            if "sharedWith" in r:
                return (
                    r
                    if not parse
                    else {
                        "friends": [Friend(friend_data=friend, logger=self._log) for friend in r["friends"]],
                        "shared_with": [Friend(friend_data=friend, logger=self._log) for friend in r["sharedWith"]],
                    }
                )
            return (
                {"friends": [Friend(friend_data=friend, logger=self._log) for friend in r["friends"]]} if parse else r
            )

        raise UnidentifiedAPIError(reason=resp)

    async def add_friend(self, name: str, phone_number: str | int, code: str | int, parse=False) -> dict | Friend:
        """Adds user friends for inpost services

        :param name: name of further inpost friend
        :type name: str
        :param phone_number: further friend phone number
        :type phone_number: str | int
        :param code: used when you have a friendship code from your friend
        :type code: str | int
        :param parse: switch for parsing response
        :type parse: bool
        :return: :class:`dict` with friends details
        :rtype: dict
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: User with specified phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        :raises ValueError: Name length exceeds 20 characters
        """

        self._log.info("adding user friend")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        if len(name) > 20:
            raise ValueError(f"Name too long: {name} (over 20 characters")

        if code:
            if isinstance(code, int):
                code = str(code)

            resp = await self.request(
                method="post",
                action="add friend",
                url=validate_friendship_url,
                auth=True,
                headers=None,
                data={"invitationCode": code},
                autorefresh=True,
            )

            if resp.status == 200:
                self._log.debug("added user friend")
                return await resp.json() if not parse else Friend(await resp.json(), logger=self._log)

        else:
            if isinstance(phone_number, int):
                phone_number = str(phone_number)

            resp = await self.request(
                method="post",
                action="add friend",
                url=friendship_url,
                auth=True,
                headers=None,
                data={"phoneNumber": phone_number, "name": name},
                autorefresh=True,
            )

            if resp.status == 200:
                self._log.debug("added user friend")
                r = await resp.json()
                if r["status"] == "AUTO_ACCEPT":
                    return (
                        {"phoneNumber": phone_number, "name": name}
                        if not parse
                        else Friend({"phoneNumber": phone_number, "name": name}, logger=self._log)
                    )

                elif r["status"] == "RETURN_INVITATION_CODE":
                    return r if not parse else Friend.from_invitation(invitation_data=r, logger=self._log)

                else:
                    self._log.warning(r)

        raise UnidentifiedAPIError(reason=resp)

    async def remove_friend(self, uuid: str | None, name: str | None, phone_number: str | int | None) -> bool:
        """Removes user friend for inpost services with specified `uuid`/`phone_number`/`name`

        :param uuid: uuid of inpost friend to remove
        :type uuid: str | None
        :param name: name of inpost friend to remove
        :type name: str | None
        :param phone_number: phone number of inpost friend to remove
        :type phone_number: str | int | None
        :return: True if friend is removed
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Friend not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        :raises ValueError: Name length exceeds 20 characters
        :raises MissingParamsError: none of required uuid, name or phone_number params are filled
        """

        self._log.info("removing user friend")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        if uuid is None and name is None and phone_number is None:
            raise MissingParamsError(reason="None of params are filled (one required)")

        if isinstance(phone_number, int):
            phone_number = str(phone_number)

        if uuid is None:
            f = await self.get_friends()
            if not isinstance(f, dict):
                return False

            if phone_number:
                uuid = next((friend["uuid"] for friend in f["friends"] if friend["phoneNumber"] == phone_number))
            else:
                uuid = next((friend["uuid"] for friend in f["friends"] if friend["name"] == name))

        resp = await self.request(
            method="delete",
            action="remove user friend",
            url=f"{friendship_url}{uuid}",
            auth=True,
            headers=None,
            data=None,
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug("removed user friend")
            return True

        return False

    async def update_friend(self, uuid: str | None, phone_number: str | int | None, name: str) -> bool:
        """Updates user friend for inpost services with specified `name`

        :param uuid: uuid of inpost friend to update
        :type uuid: str | None
        :param name: new name of inpost friend
        :type name: str
        :param phone_number: phone number of inpost friend to update
        :type phone_number: str | int | None
        :return: True if friend is updated
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Friend not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        :raises ValueError: Name length exceeds 20 characters
        """

        self._log.info("updating user friend")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        if len(name) > 20:
            raise ValueError(f"Name too long: {name} (over 20 characters")

        if isinstance(phone_number, int):
            phone_number = str(phone_number)

        if uuid is None:
            obtained_friends = await self.get_friends()
            if not isinstance(obtained_friends, dict):
                return False

            uuid = next((friend["uuid"] for friend in obtained_friends if friend["phoneNumber"] == phone_number))

        resp = await self.request(
            method="patch",
            action="update user friend",
            url=f"{friendship_url}{uuid}",
            auth=True,
            headers=None,
            data=None,
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug("updated user friend")
            return True

        return False

    async def share_parcel(self, uuid: str, shipment_number: int | str) -> bool:
        """Shares parcel to a pre-initialized friend

        :param uuid: uuid of inpost friend to update
        :type uuid: str
        :param shipment_number: Parcel's shipment number
        :type shipment_number: int | str
        :return: True if parcel is shared
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        self._log.info(f"sharing parcel: {shipment_number}")

        if not self.auth_token:
            self._log.debug("authorization token missing")
            raise NotAuthenticatedError(reason="Not logged in")

        resp = await self.request(
            method="post",
            action=f"share parcel: {shipment_number}",
            url=shared_url,
            auth=True,
            headers=None,
            data={
                "parcels": [{"shipmentNumber": shipment_number, "friendUuids": [uuid]}],
            },
            autorefresh=True,
        )

        if resp.status == 200:
            self._log.debug("updated user friend")
            return True

        return False
