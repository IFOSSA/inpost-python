from typing import Union, List

from aiohttp import ClientSession
from static.endpoints import *
from static.headers import appjson
from static.exceptions import *
from static.parcels import Parcel


class Inpost:
    def __init__(self, phone_number: str):
        self.phone_number: str = phone_number
        self.sms_code: str | None = None
        self.auth_token: str | None = None
        self.refr_token: str | None = None
        self.sess: ClientSession = ClientSession()

    def __repr__(self):
        return f'Username: {self.phone_number}\nToken: {self.auth_token}'

    async def send_sms_code(self) -> Optional[bool]:
        async with await self.sess.post(url=send_sms_code,
                                        json={
                                            'phoneNumber': f'{self.phone_number}'
                                        }) as phone:
            if phone.status == 200:
                return True
            else:
                raise PhoneNumberError(phone)

    async def confirm_sms_code(self, sms_code: str):
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

        return False

    async def refresh_token(self):
        if not self.auth_token:
            raise NotAuthenticatedError(reason='Authentication token missing')

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

    async def logout(self):
        if self.auth_token is not None:
            async with await self.sess.post(url=logout,
                                            headers={'Authorization': self.auth_token}) as resp:
                if resp.status == 200:
                    print(await resp.text())
                    self.auth_token = None
                else:
                    raise SomeAPIError(reason=resp)
        else:
            raise NotAuthenticatedError(reason='Not logged in')

    async def disconnect(self):
        await self.logout()
        await self.sess.close()

    async def get_parcel(self, shipment_number: Union[int, str], parse=False) -> Union[dict, Parcel]:
        if not self.auth_token:
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.get(url=f"{parcel}{shipment_number}",
                                       headers={'Authorization': self.auth_token},
                                       ) as resp:
            if resp.status == 200:
                return await resp.json() if not parse else Parcel(await resp.json())

            else:
                raise SomeAPIError(reason=resp)

    async def get_parcels(self, as_list=False) -> Union[dict, List[Parcel]]:
        if not self.auth_token:
            raise NotAuthenticatedError(reason='Not logged in')

        async with await self.sess.get(url=parcels,
                                       headers={'Authorization': self.auth_token},
                                       ) as resp:
            if resp.status == 200:
                x = await resp.json()
                return await resp.json() if not as_list else [Parcel(parcel_data=data) for data in
                                                              (await resp.json())['parcels']]

            else:
                raise SomeAPIError(reason=resp)

    # async def send_parcel(self,
    #                       recipient_email: str,
    #                       recipient_phone_number: str,
    #                       parcel_type: ParcelDeliveryType,
    #                       parcel_size: Union[ParcelLockerSize, ParcelCarrierSize],  # only for parcel locker
    #                       parcel_locker_code: Optional[str],
    #                       shipment_method: ParcelShipmentType,
    #                       referral_number: Optional[str],
    #                       name: str,
    #                       bussines_name: str,
    #                       zip_code: str,
    #                       city: str,
    #                       street: str,
    #                       building_number: int,
    #                       apartment_numer: int,
    #                       charge_value: Optional[int],
    #                       end_of_week_collection: Optional[bool]):
    #     if not self.auth_token:
    #         raise NotAuthenticatedError
    #
    #     raise NotImplementedError
    #
    # async def new_parcel(self):
    #     if not self.auth_token:
    #         raise NotAuthenticatedError
    #
    #     raise NotImplementedError
