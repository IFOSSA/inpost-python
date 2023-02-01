from aiohttp import ClientSession
from typing import List
import logging

from inpost.static import *


class Inpost:
    """Python representation of an Inpost app. Essentially implements methods to manage all incoming parcels"""

    def __init__(self):
        """Constructor method"""
        self.phone_number: str | None = None
        self.sms_code: str | None = None
        self.auth_token: str | None = None
        self.refr_token: str | None = None
        self.sess: ClientSession = ClientSession()
        self.parcel: Parcel | None = None
        self._log: logging.Logger | None = None

    def __repr__(self):
        return f'{self.__class__.__name__}(phone_number={self.phone_number})'

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.logout()

    @classmethod
    async def from_phone_number(cls, phone_number: str | int):
        """`Classmethod` to initialize :class:`Inpost` object with phone number

        :param phone_number: User's Inpost phone number
        :type phone_number: str | int"""
        if isinstance(phone_number, int):
            phone_number = str(phone_number)
        inp = cls()
        await inp.set_phone_number(phone_number=phone_number)
        inp._log.info(f'initialized by from_phone_number')
        return inp

    async def set_phone_number(self, phone_number: str | int) -> bool:
        """Set :class:`Inpost` phone number required for verification

        :param phone_number: User's Inpost phone number
        :type phone_number: str | int
        :return: True if `Inpost.phone_number` is set
        :rtype: bool
        :raises PhoneNumberError: Wrong phone number format"""
        if isinstance(phone_number, int):
            phone_number = str(phone_number)

        if len(phone_number) == 9 and phone_number.isdigit():
            self._log = logging.getLogger(f'{__class__.__name__}.{phone_number}')
            self._log.setLevel(level=logging.DEBUG)
            self._log.info(f'initializing inpost object with phone number {phone_number}')
            self.phone_number = phone_number
            return True

        raise PhoneNumberError(f'Wrong phone number format: {phone_number} (should be 9 digits)')

    async def send_sms_code(self) -> bool:
        """Sends sms code to `Inpost.phone_number`

        :return: True if sms code sent
        :rtype: bool
        :raises PhoneNumberError: Missing phone number
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected things happened
        """
        if not self.phone_number:  # can't log it cuz if there's no phone number no logger initialized @shrug
            raise PhoneNumberError('Phone number missing')

        self._log.info(f'sending sms code')
        async with await self.sess.post(url=send_sms_code,
                                        json={
                                            'phoneNumber': f'{self.phone_number}'
                                        }) as phone:
            match phone.status:
                case 200:
                    self._log.debug(f'sms code sent')
                    return True
                case 401:
                    self._log.error(f'could not send sms code, unauthorized')
                    raise UnauthorizedError(reason=phone)
                case 404:
                    self._log.error(f'could not send sms code, not found')
                    raise NotFoundError(reason=phone)
                case _:
                    self._log.error(f'could not send sms code, unhandled status')

            raise UnidentifiedAPIError(reason=phone)

    async def confirm_sms_code(self, sms_code: str | int) -> bool:
        """Confirms sms code sent to `Inpost.phone_number` and fetches tokens

        :param sms_code: sms code sent to Inpost.phone_number device
        :type sms_code: str | int
        :return: True if sms code gets confirmed and tokens fetched
        :rtype: bool
        :raises SmsCodeError: Wrong sms code format
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """

        if not self.phone_number:  # can't log it cuz if there's no phone number no logger initialized @shrug
            raise PhoneNumberError('Phone number missing')

        if isinstance(sms_code, int):
            sms_code = str(sms_code)

        if len(sms_code) != 6 or not sms_code.isdigit():
            raise SmsCodeError(reason=f'Wrong sms code format: {sms_code} (should be 6 digits)')

        self._log.info(f'confirming sms code')
        async with await self.sess.post(url=confirm_sms_code,
                                        headers=appjson,
                                        json={
                                            "phoneNumber": self.phone_number,
                                            "smsCode": sms_code,
                                            "phoneOS": "Android"
                                        }) as confirmation:
            match confirmation.status:
                case 200:
                    resp = await confirmation.json()
                    self.sms_code = sms_code
                    self.refr_token = resp['refreshToken']
                    self.auth_token = resp['authToken']
                    self._log.debug(f'sms code confirmed')
                    return True
                case 401:
                    self._log.error(f'could not confirm sms code, unauthorized')
                    raise UnauthorizedError(reason=confirmation)
                case 404:
                    self._log.error(f'could not confirm sms code, not found')
                    raise NotFoundError(reason=confirmation)
                case _:
                    self._log.error(f'could not confirm sms code, unhandled status')

            raise UnidentifiedAPIError(reason=confirmation)

    async def refresh_token(self) -> bool:
        """Refreshes authorization token using refresh token

        :return: True if Inpost.auth_token gets refreshed
        :rtype: bool
        :raises RefreshTokenError: Missing refresh token
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened
        """
        self._log.info(f'refreshing token')

        if not self.refr_token:
            self._log.error(f'refresh token missing')
            raise RefreshTokenError(reason='Refresh token missing')

        async with await self.sess.post(url=refresh_token,
                                        headers=appjson,
                                        json={
                                            "refreshToken": self.refr_token,
                                            "phoneOS": "Android"
                                        }) as confirmation:
            match confirmation.status:
                case 200:
                    resp = await confirmation.json()
                    if resp['reauthenticationRequired']:
                        self._log.error(f'could not refresh token, log in again')
                        raise ReAuthenticationError(reason='You need to log in again!')

                    self.auth_token = resp['authToken']
                    self._log.debug(f'token refreshed')
                    return True
                case 401:
                    self._log.error(f'could not refresh token, unauthorized')
                    raise UnauthorizedError(reason=confirmation)
                case 404:
                    self._log.error(f'could not refresh token, not found')
                    raise NotFoundError(reason=confirmation)
                case _:
                    self._log.error(f'could not refresh token, unhandled status')

            raise UnidentifiedAPIError(reason=confirmation)

    async def logout(self) -> bool:
        """Logouts user from inpost api service

        :return: True if the user is logged out
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened"""
        self._log.info(f'logging out')

        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.post(url=logout,
                                        headers={'Authorization': self.auth_token}) as resp:
            match resp.status:
                case 200:
                    self.phone_number = None
                    self.refr_token = None
                    self.auth_token = None
                    self.sms_code = None
                    self._log.debug('logged out')
                    return True
                case 401:
                    self._log.error('could not log out, unauthorized')
                    raise UnauthorizedError(reason=resp)
                case 404:
                    self._log.error('could not log out, not found')
                    raise NotFoundError(reason=resp)
                case _:
                    self._log.error('could not log out, unhandled status')

            raise UnidentifiedAPIError(reason=resp)

    async def disconnect(self) -> bool:
        """Simplified method to logout and close user's session

        :return: True if user is logged out and session is closed else False
        :raises NotAuthenticatedError: User not authenticated in inpost service"""
        self._log.info(f'disconnecting')
        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        if await self.logout():
            await self.sess.close()
            self._log.debug(f'disconnected')
            return True

        self._log.error('could not disconnect')
        return False

    async def get_parcel(self, shipment_number: int | str, parse=False) -> dict | Parcel:
        """Fetches single parcel from provided shipment number

        :param shipment_number: Parcel's shipment number
        :type shipment_number: int | str
        :param parse: if set to True method will return :class:`Parcel` else :class:`dict`
        :type parse: bool
        :return: Fetched parcel data
        :rtype: dict | Parcel
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened"""
        self._log.info(f'getting parcel with shipment number: {shipment_number}')

        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.get(url=f"{parcel}{shipment_number}",
                                       headers={'Authorization': self.auth_token},
                                       ) as resp:
            match resp.status:
                case 200:
                    self._log.debug(f'parcel with shipment number {shipment_number} received')
                    return await resp.json() if not parse else Parcel(await resp.json(), logger=self._log)
                case 401:
                    self._log.error(f'could not get parcel with shipment number {shipment_number}, unauthorized')
                    raise UnauthorizedError(reason=resp)
                case 404:
                    self._log.error(f'could not get parcel with shipment number {shipment_number}, not found')
                    raise NotFoundError(reason=resp)
                case _:
                    self._log.error(f'could not get parcel with shipment number {shipment_number}, unhandled status')

            raise UnidentifiedAPIError(reason=resp)

    async def get_parcels(self,
                          parcel_type: ParcelType = ParcelType.TRACKED,
                          status: ParcelStatus | List[ParcelStatus] | None = None,
                          pickup_point: str | List[str] | None = None,
                          shipment_type: ParcelShipmentType | List[ParcelShipmentType] | None = None,
                          parcel_size: ParcelLockerSize | ParcelCarrierSize | None = None,
                          parse: bool = False) -> List[dict] | List[Parcel]:
        """Fetches all available parcels for set `Inpost.phone_number` and optionally filters them

        :param parcel_type: Parcel type (e.g. received, sent, returned)
        :type parcel_type: ParcelType
        :param status: status that each fetched parcels has to be in
        :type status: ParcelStatus | list[ParcelStatus] | None
        :param pickup_point: Fetched parcels have to be picked from this pickup point (e.g. `GXO05M`)
        :type pickup_point: str | list[str] | None
        :param shipment_type: Fetched parcels have to be shipped that way
        :type shipment_type: ParcelShipmentType | list[ParcelShipmentType] | None
        :param parcel_size: Fetched parcels have to be this size
        :type parcel_size: ParcelLockerSize | ParcelCarrierSize | None
        :param parse: if set to True method will return list[:class:`Parcel`] else list[:class:`dict`]
        :type parse: bool
        :return: fetched parcels data
        :rtype: list[dict] | list[Parcel]
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises ParcelTypeError: Unknown parcel type selected
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened"""
        self._log.info('getting parcels')

        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        if not isinstance(parcel_type, ParcelType):
            self._log.error(f'wrong parcel type {parcel_type}')
            raise ParcelTypeError(reason=f'Unknown parcel type: {parcel_type}')

        match parcel_type:
            case ParcelType.TRACKED:
                self._log.debug(f'getting parcel type {parcel_type}')
                url = parcels
            case ParcelType.SENT:
                self._log.debug(f'getting parcel type {parcel_type}')
                url = sent
            case ParcelType.RETURNS:
                self._log.debug(f'getting parcel type {parcel_type}')
                url = returns
            case _:
                self._log.error(f'wrong parcel type {parcel_type}')
                raise ParcelTypeError(reason=f'Unknown parcel type: {parcel_type}')

        async with await self.sess.get(url=url,
                                       headers={'Authorization': self.auth_token},
                                       ) as resp:
            match resp.status:
                case 200:
                    self._log.debug(f'received {parcel_type} parcels')
                    _parcels = (await resp.json())['parcels']

                    if status is not None:
                        if isinstance(status, ParcelStatus):
                            status = [status]

                        _parcels = (_parcel for _parcel in _parcels if ParcelStatus[_parcel['status']] in status)

                    if pickup_point is not None:
                        if isinstance(pickup_point, str):
                            pickup_point = [pickup_point]

                        _parcels = (_parcel for _parcel in _parcels if
                                    _parcel['pickUpPoint']['name'] in pickup_point)

                    if shipment_type is not None:
                        if isinstance(shipment_type, ParcelShipmentType):
                            shipment_type = [shipment_type]

                        _parcels = (_parcel for _parcel in _parcels if
                                    ParcelShipmentType[_parcel['shipmentType']] in shipment_type)

                    if parcel_size is not None:
                        if isinstance(parcel_size, ParcelCarrierSize):
                            parcel_size = [parcel_size]

                            _parcels = (_parcel for _parcel in _parcels if
                                        ParcelCarrierSize[_parcel['parcelSize']] in parcel_size)

                        if isinstance(parcel_size, ParcelLockerSize):
                            parcel_size = [parcel_size]

                            _parcels = (_parcel for _parcel in _parcels if
                                        ParcelLockerSize[_parcel['parcelSize']] in parcel_size)

                    return _parcels if not parse else [Parcel(parcel_data=data, logger=self._log) for data in
                                                       _parcels]
                case 401:
                    self._log.error(f'could not get parcels, unauthorized')
                    raise UnauthorizedError(reason=resp)
                case 404:
                    self._log.error(f'could not get parcels, not found')
                    raise NotFoundError(reason=resp)
                case _:
                    self._log.error(f'could not get parcels, unhandled status')

            raise UnidentifiedAPIError(reason=resp)

    async def get_multi_compartment(self, multi_uuid: str | int, parse: bool = False) -> dict | List[Parcel]:
        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.get(url=f"{multi}{multi_uuid}",
                                       headers={'Authorization': self.auth_token},
                                       ) as resp:
            match resp.status:
                case 200:
                    self._log.debug(f'parcel with multicompartment uuid {multi_uuid} received')
                    return await resp.json() if not parse else [Parcel(data, logger=self._log) for data in (await resp.json())['parcels']]
                case 401:
                    self._log.error(f'could not get parcel with multicompartment uuid {multi_uuid}, unauthorized')
                    raise UnauthorizedError(reason=resp)
                case 404:
                    self._log.error(f'could not get parcel with multicompartment uuid {multi_uuid}, not found')
                    raise NotFoundError(reason=resp)
                case _:
                    self._log.error(f'could not get parcel with multicompartment uuid {multi_uuid}, unhandled status')

            raise UnidentifiedAPIError(reason=resp)

    async def collect_compartment_properties(self, shipment_number: str | int | None = None,
                                             parcel_obj: Parcel | None = None, location: dict | None = None) -> bool:
        """Validates sent data and fetches required compartment properties for opening

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
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened

        .. warning:: you must fill in only one parameter - shipment_number or parcel_obj!"""

        if shipment_number and parcel_obj:
            self._log.error(f'shipment_number and parcel_obj filled in')
            raise SingleParamError(reason='Fields shipment_number and parcel_obj filled in! Choose one!')

        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        if shipment_number is not None and parcel_obj is None:
            self._log.debug(f'parcel_obj not provided, getting from shipment number {shipment_number}')
            parcel_obj = await self.get_parcel(shipment_number=shipment_number, parse=True)

        self._log.info(f'collecting compartment properties for {parcel_obj.shipment_number}')

        async with await self.sess.post(url=collect,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'parcel': parcel_obj.compartment_open_data,
                                            'geoPoint': location if location is not None else parcel_obj.mocked_location
                                        }) as collect_resp:
            match collect_resp.status:
                case 200:
                    self._log.debug(f'collected compartment properties for {parcel_obj.shipment_number}')
                    parcel_obj.compartment_properties = await collect_resp.json()
                    self.parcel = parcel_obj
                    return True
                case 401:
                    self._log.error(f'could not collect compartment properties for {parcel_obj.shipment_number}, '
                                    f'unauthorized')
                    raise UnauthorizedError(reason=collect_resp)
                case 404:
                    self._log.error(f'could not collect compartment properties for {parcel_obj.shipment_number}, not '
                                    f'found')
                    raise NotFoundError(reason=collect_resp)
                case _:
                    self._log.error(f'could not collect compartment properties for {parcel_obj.shipment_number}, '
                                    f'unhandled status')

            raise UnidentifiedAPIError(reason=collect_resp)

    async def open_compartment(self) -> bool:
        """Opens compartment for `Inpost.parcel` object

        :return: True if compartment gets opened
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened"""
        self._log.info(f'opening compartment for {self.parcel.shipment_number}')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.post(url=compartment_open,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'sessionUuid': self.parcel.compartment_properties.session_uuid
                                        }) as compartment_open_resp:
            match compartment_open_resp.status:
                case 200:
                    self._log.debug(f'opened comaprtment for {self.parcel.shipment_number}')
                    self.parcel.compartment_properties.location = await compartment_open_resp.json()
                    return True
                case 401:
                    self._log.error(f'could not open compartment for {self.parcel.shipment_number}, unauthorized')
                    raise UnauthorizedError(reason=compartment_open_resp)
                case 404:
                    self._log.error(f'could not open compartment for {self.parcel.shipment_number}, not found')
                    raise NotFoundError(reason=compartment_open_resp)
                case _:
                    self._log.error(f'could not open compartment for {self.parcel.shipment_number}, unhandled status')

            raise UnidentifiedAPIError(reason=compartment_open_resp)

    async def check_compartment_status(self,
                                       expected_status: CompartmentExpectedStatus = CompartmentExpectedStatus.OPENED) -> bool:
        """Checks and compare compartment status (e.g. opened, closed) with expected status

        :param expected_status: Compartment expected status
        :type expected_status: CompartmentExpectedStatus
        :return: True if actual status equals expected status else False
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened"""
        self._log.info(f'checking compartment status for {self.parcel.shipment_number}')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        if not self.parcel:
            self._log.debug(f'parcel missing')
            raise NoParcelError(reason='Parcel is not set')

        async with await self.sess.post(url=compartment_status,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'sessionUuid': self.parcel.compartment_properties.session_uuid,
                                            'expectedStatus': expected_status.name
                                        }) as compartment_status_resp:
            match compartment_status_resp.status:
                case 200:
                    self._log.debug(f'checked compartment status for {self.parcel.shipment_number}')
                    self.parcel.compartment_status = (await compartment_status_resp.json())['status']
                    return CompartmentExpectedStatus[
                        (await compartment_status_resp.json())['status']] == expected_status
                case 401:
                    self._log.error(
                        f'could not check compartment status for {self.parcel.shipment_number}, unauthorized')
                    raise UnauthorizedError(reason=compartment_status_resp)
                case 404:
                    self._log.error(f'could not check compartment status for {self.parcel.shipment_number}, not found')
                    raise NotFoundError(reason=compartment_status_resp)
                case _:
                    self._log.error(
                        f'could not check compartment status for {self.parcel.shipment_number}, unhandled status')

            raise UnidentifiedAPIError(reason=compartment_status_resp)

    async def terminate_collect_session(self) -> bool:
        """Terminates user session in inpost api service

        :return: True if the user session is terminated
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened"""
        self._log.info(f'terminating collect session for {self.parcel.shipment_number}')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.post(url=terminate_collect_session,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'sessionUuid': self.parcel.compartment_properties.session_uuid
                                        }) as terminate_resp:
            match terminate_resp.status:
                case 200:
                    self._log.debug(f'terminated collect session for {self.parcel.shipment_number}')
                    return True
                case 401:
                    self._log.error(
                        f'could not terminate collect session for {self.parcel.shipment_number}, unauthorized')
                    raise UnauthorizedError(reason=terminate_resp)
                case 404:
                    self._log.error(f'could not terminate collect session for {self.parcel.shipment_number}, not found')
                    raise NotFoundError(reason=terminate_resp)
                case _:
                    self._log.error(
                        f'could not terminate collect session for {self.parcel.shipment_number}, unhandled status')

            raise UnidentifiedAPIError(reason=terminate_resp)

    async def collect(self, shipment_number: str | None = None, parcel_obj: Parcel | None = None,
                      location: dict | None = None) -> bool:
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
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened

        .. warning:: you must fill in only one parameter - shipment_number or parcel_obj!"""

        if shipment_number and parcel_obj:
            self._log.error(f'shipment_number and parcel_obj filled in')
            raise SingleParamError(reason='Fields shipment_number and parcel_obj filled! Choose one!')

        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        if shipment_number is not None and parcel_obj is None:
            parcel_obj = await self.get_parcel(shipment_number=shipment_number, parse=True)

        self._log.info(f'collecing parcel with shipment number {parcel_obj.shipment_number}')

        if await self.collect_compartment_properties(parcel_obj=parcel_obj, location=location):
            if await self.open_compartment():
                if await self.check_compartment_status():
                    return True

        return False

    async def close_compartment(self) -> bool:
        """Checks whether actual compartment status and expected one matches then notifies inpost api that compartment is closed

        :return: True if compartment status is closed and successfully terminates user's session else False
        :rtype: bool"""
        self._log.info(f'closing compartment for {self.parcel.shipment_number}')

        if await self.check_compartment_status(expected_status=CompartmentExpectedStatus.CLOSED):
            if await self.terminate_collect_session():
                return True

        return False

    async def get_prices(self) -> dict:
        """Fetches prices for inpost services

        :return: :class:`dict` of prices for inpost services
        :rtype: dict
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened"""
        self._log.info(f'getting parcel prices')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.get(url=parcel_prices,
                                       headers={'Authorization': self.auth_token}) as resp:
            match resp.status:
                case 200:
                    self._log.debug(f'got parcel prices')
                    return await resp.json()
                case 401:
                    self._log.error('could not get parcel prices, unauthorized')
                    raise UnauthorizedError(reason=resp)
                case 404:
                    self._log.error('could not get parcel prices, not found')
                    raise NotFoundError(reason=resp)
                case _:
                    self._log.error('could not get parcel prices, unhandled status')

            raise UnidentifiedAPIError(reason=resp)
