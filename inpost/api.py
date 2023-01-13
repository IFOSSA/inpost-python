from aiohttp import ClientSession
from typing import List
import logging

from inpost.static import *


class Inpost:
    def __init__(self):
        self.phone_number: str | None = None
        self.sms_code: str | None = None
        self.auth_token: str | None = None
        self.refr_token: str | None = None
        self.sess: ClientSession = ClientSession()
        self.parcel: Parcel | None = None
        self._log: logging.Logger | None = None

    def __repr__(self):
        return f'Phone number: {self.phone_number}\nToken: {self.auth_token}'

    async def set_phone_number(self, phone_number: str) -> bool | None:
        self._log = logging.getLogger(f'{__class__.__name__}.{phone_number}')
        self._log.setLevel(level=logging.DEBUG)
        self._log.info(f'initializing inpost object with phone number {phone_number}')
        self.phone_number = phone_number
        return True

    async def send_sms_code(self) -> bool | None:
        if not self.phone_number:  # can't log it cuz if there's no phone number no logger initialized @shrug
            raise PhoneNumberError('Phone number missing')

        self._log.info(f'sending sms code')
        async with await self.sess.post(url=send_sms_code,
                                        json={
                                            'phoneNumber': f'{self.phone_number}'
                                        }) as phone:
            if phone.status == 200:
                self._log.debug(f'sms code sent')
                return True
            else:
                self._log.error(f'could not sent sms code')
                raise PhoneNumberError(reason=phone)

    async def confirm_sms_code(self, sms_code: str) -> bool | None:
        if not self.phone_number:  # can't log it cuz if there's no phone number no logger initialized @shrug
            raise PhoneNumberError('Phone number missing')

        self._log.info(f'confirming sms code')
        async with await self.sess.post(url=confirm_sms_code,
                                        headers=appjson,
                                        json={
                                            "phoneNumber": self.phone_number,
                                            "smsCode": sms_code,
                                            "phoneOS": "Android"
                                        }) as confirmation:
            if confirmation.status == 200:
                resp = await confirmation.json()
                self.sms_code = sms_code
                self.refr_token = resp['refreshToken']
                self.auth_token = resp['authToken']
                self._log.debug(f'sms code confirmed')
                return True
            else:
                self._log.error(f'could not confirm sms code')
                raise SmsCodeConfirmationError(reason=confirmation)

    async def refresh_token(self) -> bool | None:
        self._log.info(f'refreshing token')

        if not self.refr_token:
            self._log.error(f'refresh token missing')
            raise NotAuthenticatedError(reason='Refresh token missing')

        async with await self.sess.post(url=refresh_token,
                                        headers=appjson,
                                        json={
                                            "refreshToken": self.refr_token,
                                            "phoneOS": "Android"
                                        }) as confirmation:
            if confirmation.status == 200:
                resp = await confirmation.json()
                if resp['reauthenticationRequired']:
                    self._log.error(f'could not reauthenticate')
                    raise ReAuthenticationError(reason='You need to log in again!')
                self.auth_token = resp['authToken']
                self._log.debug(f'token refreshed')
                return True

            else:
                self._log.error(f'error: {confirmation}')
                raise RefreshTokenException(reason=confirmation)

    async def logout(self) -> bool | None:
        self._log.info(f'logging out')

        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.post(url=logout,
                                        headers={'Authorization': self.auth_token}) as resp:
            if resp.status == 200:
                self.phone_number = None
                self.refr_token = None
                self.auth_token = None
                self.sms_code = None
                return True
            else:
                raise UnidentifiedAPIError(reason=resp)

    async def disconnect(self) -> bool:
        self._log.info(f'disconnecting')
        if await self.logout():
            await self.sess.close()
            self._log.debug(f'refreshing disconnected')
            return True

        return False

    async def get_parcel(self, shipment_number: int | str, parse=False) -> dict | Parcel:
        self._log.info(f'getting parcel with shipment number: {shipment_number}')

        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.get(url=f"{parcel}{shipment_number}",
                                       headers={'Authorization': self.auth_token},
                                       ) as resp:
            if resp.status == 200:
                self._log.debug(f'parcel with shipment number {shipment_number} received')
                return await resp.json() if not parse else Parcel(await resp.json(), logger=self._log)

            else:
                self._log.error(f'could not get parcel with shipment number {shipment_number}')
                raise UnidentifiedAPIError(reason=resp)

    async def get_parcels(self,
                          parcel_type: ParcelType = ParcelType.TRACKED,
                          status: ParcelStatus | List[ParcelStatus] | None = None,
                          pickup_point: str | List[str] | None = None,
                          shipment_type: ParcelShipmentType | List[ParcelShipmentType] | None = None,
                          parcel_size: ParcelLockerSize | ParcelCarrierSize | None = None,
                          parse: bool = False) -> List[dict] | List[Parcel]:
        self._log.info('getting parcels')
        if not self.auth_token:
            self._log.error(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        if not isinstance(parcel_type, ParcelType):
            self._log.error(f'wrong parcel type {parcel_type}')
            raise ParcelTypeError(reason=f'Unknown parcel type: {parcel_type}')

        match parcel_type:
            case ParcelType.TRACKED:
                url = parcels
            case ParcelType.SENT:
                url = sent
            case ParcelType.RETURNS:
                url = returns
            case _:
                self._log.error(f'wrong parcel type {parcel_type}')
                raise ParcelTypeError(reason=f'Unknown parcel type: {parcel_type}')

        async with await self.sess.get(url=url,
                                       headers={'Authorization': self.auth_token},
                                       ) as resp:
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

                    _parcels = (_parcel for _parcel in _parcels if _parcel['pickUpPoint']['name'] in pickup_point)

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

                return _parcels if not parse else [Parcel(parcel_data=data, logger=self._log) for data in _parcels]

            else:
                self._log.error(f'could not get parcels')
                raise UnidentifiedAPIError(reason=resp)

    async def collect_compartment_properties(self, shipment_number: str | None = None, parcel_obj: Parcel | None = None,
                                             location: dict | None = None) -> bool:
        self._log.info(f'collecting compartment properties for {shipment_number}')
        if shipment_number is not None and parcel_obj is None:
            self._log.debug(f'parcel_obj not provided, getting from shipment number {shipment_number}')
            parcel_obj = await self.get_parcel(shipment_number=shipment_number, parse=True)

        async with await self.sess.post(url=collect,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'parcel': parcel_obj.compartment_open_data,
                                            'geoPoint': location if location is not None else parcel_obj.mocked_location
                                        }) as collect_resp:
            if collect_resp.status == 200:
                self._log.debug(f'collected compartment properties for {shipment_number}')
                parcel_obj.compartment_properties = await collect_resp.json()
                self.parcel = parcel_obj
                return True

            else:
                self._log.error(f'could not collect compartment properties for {shipment_number}')
                raise UnidentifiedAPIError(reason=collect_resp)

    async def open_compartment(self):
        async with await self.sess.post(url=compartment_open,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'sessionUuid': self.parcel.compartment_properties.session_uuid
                                        }) as compartment_open_resp:
            if compartment_open_resp.status == 200:
                self._log.debug(f'opened comaprtment for {self.parcel.shipment_number}')
                self.parcel.compartment_properties.location = await compartment_open_resp.json()
                return True

            else:
                self._log.error(f'could not open compartment for {self.parcel.shipment_number}')
                raise UnidentifiedAPIError(reason=compartment_open_resp)

    async def check_compartment_status(self,
                                       expected_status: CompartmentExpectedStatus = CompartmentExpectedStatus.OPENED):
        self._log.info(f'checking compartment status for {self.parcel.shipment_number}')

        async with await self.sess.post(url=compartment_status,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'sessionUuid': self.parcel.compartment_properties.session_uuid,
                                            'expectedStatus': expected_status.name
                                        }) as compartment_status_resp:
            if compartment_status_resp.status == 200:
                self._log.debug(f'checked compartment status for {self.parcel.shipment_number}')
                return CompartmentExpectedStatus[(await compartment_status_resp.json())['status']] == expected_status
            else:
                self._log.error(f'could not check compartment status for {self.parcel.shipment_number}')
                raise UnidentifiedAPIError(reason=compartment_status_resp)

    async def terminate_collect_session(self):
        self._log.info(f'terminating collect session for {self.parcel.shipment_number}')

        async with await self.sess.post(url=terminate_collect_session,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'sessionUuid': self.parcel.compartment_properties.session_uuid
                                        }) as terminate_resp:
            if terminate_resp.status == 200:
                self._log.debug(f'terminated collect session for {self.parcel.shipment_number}')
                return True
            else:
                self._log.error(f'could not terminate collect session for {self.parcel.shipment_number}')
                raise UnidentifiedAPIError(reason=terminate_resp)

    async def collect(self, shipment_number: str | None = None, parcel_obj: Parcel | None = None,
                      location: dict | None = None) -> bool:
        self._log.info(f'collecing parcel with shipment number {self.parcel.shipment_number}')

        if shipment_number is not None and parcel_obj is None:
            parcel_obj = await self.get_parcel(shipment_number=shipment_number, parse=True)

        if await self.collect_compartment_properties(parcel_obj=parcel_obj, location=location):
            if await self.open_compartment():
                if await self.check_compartment_status():
                    return True

        return False

    async def close_compartment(self) -> bool:
        self._log.info(f'closing compartment for {self.parcel.shipment_number}')

        if await self.check_compartment_status(expected_status=CompartmentExpectedStatus.CLOSED):
            if await self.terminate_collect_session():
                return True

        return False

    async def get_prices(self) -> dict:
        self._log.info(f'getting parcel prices')

        if not self.auth_token:
            self._log.debug(f'authorization token missing')
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.get(url=parcel_prices,
                                       headers={'Authorization': self.auth_token}) as resp:
            if resp.status == 200:
                self._log.debug(f'got parcel prices')
                return await resp.json()

            else:
                raise UnidentifiedAPIError(reason=resp)
