import logging
from typing import List

from aiohttp import ClientSession, ClientResponse
from aiohttp.typedefs import StrOrURL

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

    async def request(
            self,
            method: str,
            action: str,
            url: StrOrURL,
            auth: bool = True,
            headers: dict | None = None,
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
                :type url: aiohttp.typedefs.StrOrURL
                :param auth: True if request should contain authorization header else False
                :type auth: bool
                :param headers: Additional headers for HTTP request (don't put authorization header here)
                :type headers: dict | None
                :param data: Data to be sent in HTTP request
                :type data: dict | None
                :param autorefresh: Let method automatically try to refresh token if API returns HTTP 401 Unauthorized status code
                :type autorefresh: bool
                :return: response of http request
                :rtype: aiohttp.ClientResponse
                :raises UnauthorizedError: User not authenticated in inpost service
                :raises NotFoundError: URL not found
                :raises UnidentifiedAPIError: Unexpected things happened"""

        if auth and headers:
            if 'Authorization' in headers:
                raise ValueError('Both auth==True and Authorization in additional headers')

        headers_ = {} if headers is None else headers

        if auth:
            headers_.update(
                {'Authorization': self.auth_token}
            )

        resp = await self.sess.request(method, url, headers=headers_, json=data, **kwargs)

        if autorefresh and resp.status == 401:
            await self.refresh_token()
            headers_.update(
                {'Authorization': self.auth_token}
            )
            resp = await self.sess.request(method, url, headers=headers_, json=data, **kwargs)

        match resp.status:
            case 200:
                self._log.debug(f'{action} done')
                return resp
            case 401:
                self._log.error(f'could not perform {action}, unauthorized')
                raise UnauthorizedError(reason=resp)
            case 404:
                self._log.error(f'could not perform {action}, not found')
                raise NotFoundError(reason=resp)
            case _:
                self._log.error(f'could not perform {action}, unhandled status')

        raise UnidentifiedAPIError(reason=resp)

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

    @classmethod
    async def from_dict(cls, data: dict):
        inp = cls()
        await inp.set_phone_number(data['phone_number'])
        inp.sms_code = data['sms_code']
        inp.auth_token = data['auth_token']
        inp.refr_token = data['refr_token']

        inp._log.info(f'initialized by from_dict')
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

        resp = await self.request(method='post',
                                  action='send sms code',
                                  url=send_sms_code,
                                  auth=False,
                                  headers=None,
                                  data={'phoneNumber': f'{self.phone_number}'},
                                  autorefresh=False)

        return True if resp.status == 200 else False

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

        resp = await self.request(method='post',
                                  action='confirm sms code',
                                  url=confirm_sms_code,
                                  auth=False,
                                  headers=appjson,
                                  data={
                                      "phoneNumber": self.phone_number,
                                      "smsCode": sms_code,
                                      "phoneOS": "Android"
                                  },
                                  autorefresh=False)

        if resp.status == 200:
            auth_token_data = await resp.json()
            self.sms_code = sms_code
            self.refr_token = auth_token_data['refreshToken']
            self.auth_token = auth_token_data['authToken']
            self._log.debug(f'sms code confirmed')
            return True
        else:
            return False

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

        resp = await self.request(method='post',
                                  action='refresh token',
                                  url=refresh_token,
                                  auth=False,
                                  headers=appjson,
                                  data={
                                      "refreshToken": self.refr_token,
                                      "phoneOS": "Android"
                                  },
                                  autorefresh=False)

        if resp.status == 200:
            confirmation = await resp.json()
            if confirmation['reauthenticationRequired']:
                self._log.error(f'could not refresh token, log in again')
                raise ReAuthenticationError(reason='You need to log in again!')

            self.auth_token = confirmation['authToken']
            self._log.debug(f'token refreshed')
            return True
        else:
            return False

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

        resp = await self.request(method='post',
                                  action='logout',
                                  url=logout,
                                  auth=True,
                                  headers=None,
                                  data=None,
                                  autorefresh=True)

        if resp.status == 200:
            self.phone_number = None
            self.refr_token = None
            self.auth_token = None
            self.sms_code = None
            self._log.debug('logged out')
            return True
        else:
            return False

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

        resp = await self.request(method='get',
                                  action=f"parcel with shipment number {shipment_number}",
                                  url=f"{parcel}{shipment_number}",
                                  auth=True,
                                  headers=None,
                                  data=None,
                                  autorefresh=True)

        if resp.status == 200:
            self._log.debug(f'parcel with shipment number {shipment_number} received')
            return await resp.json() if not parse else Parcel(await resp.json(), logger=self._log)

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

        resp = await self.request(method='get',
                                  action='get parcels',
                                  url=url,
                                  auth=True,
                                  headers=None,
                                  data=None,
                                  autorefresh=True)

        if resp.status == 200:
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

            return list(_parcels) if not parse else [Parcel(parcel_data=data, logger=self._log) for data in _parcels]

    async def get_multi_compartment(self, multi_uuid: str | int, parse: bool = False) -> dict | List[Parcel]:
        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        resp = await self.request(method='get',
                                  action=f"parcel with multicompartment uuid {multi_uuid}",
                                  url=f"{multi}{multi_uuid}",
                                  auth=True,
                                  headers=None,
                                  data=None,
                                  autorefresh=True)

        if resp.status == 200:
            self._log.debug(f'parcel with multicompartment uuid {multi_uuid} received')
            return (await resp.json())['parcels'] if not parse else [Parcel(data, logger=self._log) for data in
                                                                     (await resp.json())['parcels']]

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

        resp = await self.request(method='post',
                                  action='collect compartment properties',
                                  url=collect,
                                  auth=True,
                                  headers=None,
                                  data={
                                      'parcel': parcel_obj.compartment_open_data,
                                      'geoPoint': location if location is not None else parcel_obj.mocked_location
                                  },
                                  autorefresh=True)

        if resp.status == 200:
            self._log.debug(f'collected compartment properties for {parcel_obj.shipment_number}')
            parcel_obj.compartment_properties = await resp.json()
            self.parcel = parcel_obj
            return True

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

        resp = await self.request(method='post',
                                  action=f"open compartment for {self.parcel.shipment_number}",
                                  url=compartment_open,
                                  auth=True,
                                  headers=None,
                                  data={'sessionUuid': self.parcel.compartment_properties.session_uuid},
                                  autorefresh=True)

        if resp.status == 200:
            self._log.debug(f'opened compartment for {self.parcel.shipment_number}')
            return True

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

        resp = await self.request(method='post',
                                  action='check compartment status',
                                  url=compartment_status,
                                  auth=True,
                                  headers=None,
                                  data={
                                      'sessionUuid': self.parcel.compartment_properties.session_uuid,
                                      'expectedStatus': expected_status.name
                                  },
                                  autorefresh=True)

        if resp.status == 200:
            self._log.debug(f'checked compartment status for {self.parcel.shipment_number}')
            self.parcel.compartment_status = (await resp.json())['status']
            return CompartmentExpectedStatus[(await resp.json())['status']] == expected_status

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

        resp = await self.request(method='post',
                                  action='terminate collect session',
                                  url=terminate_collect_session,
                                  auth=True,
                                  headers=None,
                                  data={
                                      'sessionUuid': self.parcel.compartment_properties.session_uuid
                                  },
                                  autorefresh=True)
        if resp.status == 200:
            self._log.debug(f'terminated collect session for {self.parcel.shipment_number}')
            return True

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

        self._log.info(f'collecting parcel with shipment number {parcel_obj.shipment_number}')

        if await self.collect_compartment_properties(parcel_obj=parcel_obj, location=location):
            if await self.open_compartment():
                if await self.check_compartment_status():
                    return True

        return False

    async def close_compartment(self) -> bool:
        """Checks whether actual compartment status and expected one matches then notifies inpost api that
        compartment is closed

        :return: True if compartment status is closed and successfully terminates user's session else False
        :rtype: bool"""
        self._log.info(f'closing compartment for {self.parcel.shipment_number}')

        if await self.check_compartment_status(expected_status=CompartmentExpectedStatus.CLOSED):
            if await self.terminate_collect_session():
                return True

        return False

    async def reopen_compartment(self) -> bool:
        """Reopens compartment for `Inpost.parcel` object

        :return: True if compartment gets reopened
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened"""
        self._log.info(f'reopening compartment for {self.parcel.shipment_number}')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        resp = await self.request(method='post',
                                  action=f"reopen compartment for {self.parcel.shipment_number}",
                                  url=compartment_open,
                                  auth=True,
                                  headers=None,
                                  data={'sessionUuid': self.parcel.compartment_properties.session_uuid},
                                  autorefresh=True)

        if resp.status == 200:
            self._log.debug(f'opened compartment for {self.parcel.shipment_number}')
            return True

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

        resp = await self.request(method='get',
                                  action='get prices',
                                  url=parcel_prices,
                                  auth=True,
                                  headers=None,
                                  data=None,
                                  autorefresh=True)
        if resp.status == 200:
            self._log.debug(f'got parcel prices')
            return await resp.json()

    async def get_friends(self, parse=False) -> dict | List[Friend]:
        """Fetches user friends for inpost services

        :param parse: switch for parsing response
        :type parse: bool
        :return: :class:`dict` of user friends for inpost services
        :rtype: dict
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Phone number not found
        :raises UnidentifiedAPIError: Unexpected thing happened"""
        self._log.info(f'getting friends')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        resp = await self.request(method='get',
                                  action='get friends',
                                  url=friendship,
                                  auth=True,
                                  headers=None,
                                  data=None,
                                  autorefresh=True)
        if resp.status == 200:
            self._log.debug(f'got user friends')
            _friends = await resp.json()
            return _friends if not parse else [Friend(friend_data=friend, logger=self._log) for friend in
                                               _friends['friends']]

    async def get_parcel_friends(self, shipment_number: int | str, parse=False) -> dict:
        self._log.info(f'getting parcel friends')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        resp = await self.request(method='get',
                                  action='get parcel friends',
                                  url=f"{friendship}{shipment_number}",
                                  auth=True,
                                  headers=None,
                                  data=None,
                                  autorefresh=True)

        if resp.status == 200:
            self._log.debug(f'got parcel friends')
            r = await resp.json()
            if 'sharedWith' in r:
                return r if not parse else {
                    'friends': [Friend(friend_data=friend, logger=self._log) for friend in r['friends']],
                    'shared_with': [Friend(friend_data=friend, logger=self._log) for friend in r['sharedWith']]}
            return r if not parse else {
                'friends': [Friend(friend_data=friend, logger=self._log) for friend in r['friends']]
            }

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
        :raises ValueError: Name length exceeds 20 characters"""

        self._log.info(f'adding user friend')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        if len(name) > 20:
            raise ValueError(f'Name too long: {name} (over 20 characters')

        if code:
            if isinstance(code, int):
                code = str(code)

            resp = await self.request(method='post',
                                      action='add friend',
                                      url=validate_friendship,
                                      auth=True,
                                      headers=None,
                                      data={'invitationCode': code},
                                      autorefresh=True)

            if resp.status == 200:
                self._log.debug(f'added user friend')
                return await resp.json() if not parse else Friend(await resp.json(), logger=self._log)

        else:
            if isinstance(phone_number, int):
                phone_number = str(phone_number)

            resp = await self.request(method='post',
                                      action='add friend',
                                      url=friendship,
                                      auth=True,
                                      headers=None,
                                      data={
                                          'phoneNumber': phone_number,
                                          'name': name
                                      },
                                      autorefresh=True)

            if resp.status == 200:
                self._log.debug(f'added user friend')
                r = await resp.json()
                if r['status'] == "AUTO_ACCEPT":
                    return {'phoneNumber': phone_number, 'name': name} if not parse \
                        else Friend({'phoneNumber': phone_number, 'name': name}, logger=self._log)

                elif r['status'] == "RETURN_INVITATION_CODE":
                    return r if not parse else Friend.from_invitation(invitation_data=r, logger=self._log)

                else:
                    self._log.debug(r)

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
        :raises ValueError: Name length exceeds 20 characters"""

        self._log.info(f'adding user friend')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        if uuid is None and name is None and phone_number is None:
            raise MissingParamsError(reason='None of params are filled (one required)')

        if isinstance(phone_number, int):
            phone_number = str(phone_number)

        if uuid is None:
            f = await self.get_friends()
            if phone_number:
                uuid = next((friend['uuid'] for friend in f['friends'] if friend['phoneNumber'] == phone_number))
            else:
                uuid = next((friend['uuid'] for friend in f['friends'] if friend['name'] == name))

        resp = await self.request(method='delete',
                                  action='remove user friend',
                                  url=f'{friendship}{uuid}',
                                  auth=True,
                                  headers=None,
                                  data=None,
                                  autorefresh=True)

        if resp.status == 200:
            self._log.debug(f'removed user friend')
            return True

        return False

    async def update_friend(self, uuid: str | None, phone_number: str | int | None, name: str):
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
        :raises ValueError: Name length exceeds 20 characters"""

        self._log.info(f'updating user friend')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        if len(name) > 20:
            raise ValueError(f'Name too long: {name} (over 20 characters')

        if isinstance(phone_number, int):
            phone_number = str(phone_number)

        if uuid is None:
            uuid = next(
                (friend['uuid'] for friend in (await self.get_friends())['friends'] if
                 friend['phoneNumber'] == phone_number))

        resp = await self.request(method='patch',
                                  action='update user friend',
                                  url=f'{friends}{uuid}',
                                  auth=True,
                                  headers=None,
                                  data=None,
                                  autorefresh=True)

        if resp.status == 200:
            self._log.debug(f'updated user friend')
            return True

        return False

    async def share_parcel(self, uuid: str, shipment_number: int | str):
        """Shares parcel to a pre-initialized friend

        :param uuid: uuid of inpost friend to update
        :type uuid: str
        :param shipment_number: Parcel's shipment number
        :type shipment_number: int | str
        :return: True if parcel is shared
        :rtype: bool
        :raises NotAuthenticatedError: User not authenticated in inpost service
        :raises UnauthorizedError: Unauthorized access to inpost services,
        :raises NotFoundError: Parcel or friend not found
        :raises UnidentifiedAPIError: Unexpected thing happened"""

        self._log.info(f'sharing parcel: {shipment_number}')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        resp = await self.request(method='post',
                                  action=f'share parcel: {shipment_number}',
                                  url=shared,
                                  auth=True,
                                  headers=None,
                                  data={'parcels': [
                                      {
                                          'shipmentNumber': shipment_number,
                                          'friendUuids': [
                                              uuid
                                          ]
                                      }
                                  ],
                                  },
                                  autorefresh=True)

        if resp.status == 200:
            self._log.debug(f'updated user friend')
            return True

        return False

    # async def get_return_parcels(self):
    #     """Fetches all available parcels for set `Inpost.phone_number`
    #
    #         :return: Fetched returned parcels data
    #         :rtype: dict | Parcel
    #         :raises NotAuthenticatedError: User not authenticated in inpost service
    #         :raises UnauthorizedError: Unauthorized access to inpost services,
    #         :raises NotFoundError: Phone number not found
    #         :raises UnidentifiedAPIError: Unexpected thing happened"""
    #     self._log.info(f'getting all returned parcels')
    #
    #     if not self.auth_token:
    #         self._log.error(f'authorization token missing')
    #         raise NotAuthenticatedError(reason='Not logged in')
    #
    #     async with await self.sess.get(url=returns,
    #                                    headers={'Authorization': self.auth_token},
    #                                    ) as resp:
    #         match resp.status:
    #             case 200:
    #                 self._log.debug(f'parcel with shipment number {shipment_number} received')
    #                 return await resp.json() if not parse else Parcel(await resp.json(), logger=self._log)
    #             case 401:
    #                 self._log.error(f'could not get parcel with shipment number {shipment_number}, unauthorized')
    #                 raise UnauthorizedError(reason=resp)
    #             case 404:
    #                 self._log.error(f'could not get parcel with shipment number {shipment_number}, not found')
    #                 raise NotFoundError(reason=resp)
    #             case _:
    #                 self._log.error(f'could not get parcel with shipment number {shipment_number}, unhandled status')
    #
    #         raise UnidentifiedAPIError(reason=resp)
