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
                raise PhoneNumberError(reason=phone)

    async def confirm_sms_code(self, sms_code: str) -> Optional[bool]:
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

    async def refresh_token(self) -> Optional[bool]:
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

    async def logout(self) -> Optional[bool]:
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
                raise SomeAPIError(reason=resp)

    async def disconnect(self) -> bool:
        if await self.logout():
            await self.sess.close()
            return True

        return False

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
                return await resp.json() if not as_list else [Parcel(parcel_data=data) for data in
                                                              (await resp.json())['parcels']]

            else:
                raise SomeAPIError(reason=resp)
