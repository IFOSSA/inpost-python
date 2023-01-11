from aiohttp import ClientSession
from typing import List

from inpost.static import *


class Inpost:
    def __init__(self):
        self.phone_number: str | None = None
        self.sms_code: str | None = None
        self.auth_token: str | None = None
        self.refr_token: str | None = None
        self.sess: ClientSession = ClientSession()
        self.parcel: Parcel | None = None

    def __repr__(self):
        return f'Phone number: {self.phone_number}\nToken: {self.auth_token}'

    async def set_phone_number(self, phone_number: str) -> bool | None:
        self.phone_number = phone_number
        return True

    async def send_sms_code(self) -> bool | None:
        async with await self.sess.post(url=send_sms_code,
                                        json={
                                            'phoneNumber': f'{self.phone_number}'
                                        }) as phone:
            if phone.status == 200:
                return True
            else:
                raise PhoneNumberError(reason=phone)

    async def confirm_sms_code(self, sms_code: str) -> bool | None:
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
                return True
            else:
                raise SmsCodeConfirmationError(reason=confirmation)

    async def refresh_token(self) -> bool | None:
        if not self.refr_token:
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
                    raise ReAuthenticationError(reason='You need to log in again!')
                self.auth_token = resp['authToken']
                return True

            else:
                raise RefreshTokenException(reason=confirmation)

    async def logout(self) -> bool | None:
        if not self.auth_token:
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
        if await self.logout():
            await self.sess.close()
            return True

        return False

    async def get_parcel(self, shipment_number: int | str, parse=False) -> dict | Parcel:
        if not self.auth_token:
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.get(url=f"{parcel}{shipment_number}",
                                       headers={'Authorization': self.auth_token},
                                       ) as resp:
            if resp.status == 200:
                return await resp.json() if not parse else Parcel(await resp.json())

            else:
                raise UnidentifiedAPIError(reason=resp)

    async def get_parcels(self,
                          parcel_type: ParcelType = ParcelType.TRACKED,
                          status: ParcelStatus | List[ParcelStatus] | None = None,
                          pickup_point: str | List[str] | None = None,
                          shipment_type: ParcelShipmentType | List[ParcelShipmentType] | None = None,
                          parcel_size: ParcelLockerSize | ParcelCarrierSize | None = None,
                          parse: bool = False) -> List[dict] | List[Parcel]:
        if not self.auth_token:
            raise NotAuthenticatedError(reason='Not logged in')

        if not isinstance(parcel_type, ParcelType):
            raise ParcelTypeError(reason=f'Unknown parcel type: {parcel_type}')

        match parcel_type:
            case ParcelType.TRACKED:
                url = parcels
            case ParcelType.SENT:
                url = sent
            case ParcelType.RETURNS:
                url = returns
            case _:
                raise ParcelTypeError(reason=f'Unknown parcel type: {parcel_type}')

        async with await self.sess.get(url=url,
                                       headers={'Authorization': self.auth_token},
                                       ) as resp:
            if resp.status == 200:
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

                return _parcels if not parse else [Parcel(parcel_data=data) for data in _parcels]

            else:
                raise UnidentifiedAPIError(reason=resp)

    async def collect_compartment_properties(self, shipment_number: str | None = None, parcel_obj: Parcel | None = None,
                                             location: dict | None = None) -> bool:

        if shipment_number is not None and parcel_obj is None:
            parcel_obj = await self.get_parcel(shipment_number=shipment_number, parse=True)

        async with await self.sess.post(url=collect,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'parcel': parcel_obj.compartment_open_data,
                                            'geoPoint': location if location is not None else parcel_obj.mocked_location
                                        }) as collect_resp:
            if collect_resp.status == 200:
                parcel_obj.compartment_properties = await collect_resp.json()
                self.parcel = parcel_obj
                return True

            else:
                raise UnidentifiedAPIError(reason=collect_resp)

    async def open_compartment(self):
        async with await self.sess.post(url=compartment_open,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'sessionUuid': self.parcel.compartment_properties.session_uuid
                                        }) as compartment_open_resp:
            if compartment_open_resp.status == 200:
                self.parcel.compartment_properties.location = await compartment_open_resp.json()
                return True

            else:
                raise UnidentifiedAPIError(reason=compartment_open_resp)

    async def check_compartment_status(self,
                                       expected_status: CompartmentExpectedStatus = CompartmentExpectedStatus.OPENED):
        async with await self.sess.post(url=compartment_status,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'sessionUuid': self.parcel.compartment_properties.session_uuid,
                                            'expectedStatus': expected_status.name
                                        }) as compartment_status_resp:
            if compartment_status_resp.status == 200:
                return CompartmentExpectedStatus[(await compartment_status_resp.json())['status']] == expected_status
            else:
                raise UnidentifiedAPIError(reason=compartment_status_resp)

    async def terminate_collect_session(self):
        async with await self.sess.post(url=terminate_collect_session,
                                        headers={'Authorization': self.auth_token},
                                        json={
                                            'sessionUuid': self.parcel.compartment_properties.session_uuid
                                        }) as terminate_resp:
            if terminate_resp.status == 200:
                return True
            else:
                raise UnidentifiedAPIError(reason=terminate_resp)

    async def collect(self, shipment_number: str | None = None, parcel_obj: Parcel | None = None,
                      location: dict | None = None) -> bool:
        if shipment_number is not None and parcel_obj is None:
            parcel_obj = await self.get_parcel(shipment_number=shipment_number, parse=True)

        if await self.collect_compartment_properties(parcel_obj=parcel_obj, location=location):
            if await self.open_compartment():
                if await self.check_compartment_status():
                    return True

        return False

    async def close_compartment(self) -> bool:
        if await self.check_compartment_status(expected_status=CompartmentExpectedStatus.CLOSED):
            if await self.terminate_collect_session():
                return True

        return False

    async def get_prices(self) -> dict:
        async with await self.sess.get(url=parcel_prices,
                                       headers={'Authorization': self.auth_token}) as resp:
            return await resp.json()
