from typing import Optional, List, Union

from aiohttp import ClientSession
from json import dumps
from static.endpoints import login, logout, get_parcels
from static.headers import appjson
from static.exceptions import NotAuthenticatedError, NotImplementedError, SomeAPIError
from static.parcels import ParcelDeliveryType, ParcelForm, ParcelCarrierSize, ParcelLockerSize, ParcelShipmentType


class Inpost:
    def __init__(self, uname: str, passwd: str):
        self.username: str = uname
        self.password: str = passwd
        self.token: str | None = None
        self.sess: ClientSession = ClientSession()

    def __repr__(self):
        return f'Username: {self.username}\nPassword: {self.password}\nToken: {self.token}'

    async def authenticate(self):
        async with await self.sess.post(url=login,
                                        headers=appjson,
                                        data=dumps({'login': self.username,
                                                    'password': self.password})) as resp:
            if resp.status == 200:
                token = await resp.json()
                self.token = token['token']
            else:
                raise NotAuthenticatedError(reason=resp)

    async def logout(self):
        if self.token is not None:
            async with await self.sess.post(url=logout,
                                            headers={'X-Authorization': f'Bearer {self.token}'}) as resp:
                if resp.status == 200:
                    print(await resp.text())
                    self.token = None
                else:
                    raise SomeAPIError(reason=resp)
        else:
            raise NotAuthenticatedError(reason='Not logged in')

    async def disconnect(self):
        await self.logout()
        await self.sess.close()

    # page=1&limit=10&filters=%5BpackType%7Beq%7Doutgoing%5D%2C%5BserviceName%7Bin%7DSTANDARD%2CSTANDARD_PARCEL_SMART%2CPASS_THRU%2CCUSTOMER_SERVICE_POINT%2CREVERSE%2CSTANDARD_COURIER%2CREVERSE_RETURN%5D%2C%5BdateFrom%7Beq%7D2022-06-16%5D%2C%5BdateTo%7Beq%7D2022-06-26%5D
    async def get_parcels(self,
                          sender: Optional[str],
                          customer_reference: Optional[str],
                          parcel_code: Optional[Union[List[str], str]],
                          service_name: Union[List[str], str],
                          status: Optional[Union[List[str], str]],
                          date_from: str,
                          date_to: str,
                          end_of_week_collection: Optional[bool],
                          parcels_type: ParcelForm = ParcelForm.INCOMING,
                          limit=20,
                          page=1):
        if not self.token:
            raise NotAuthenticatedError

        raise NotImplementedError

    async def send_parcel(self,
                          recipient_email: str,
                          recipient_phone_number: str,
                          parcel_type: ParcelDeliveryType,
                          parcel_size: Union[ParcelLockerSize, ParcelCarrierSize],  # only for parcel locker
                          parcel_locker_code: Optional[str],
                          shipment_method: ParcelShipmentType,
                          referral_number: Optional[str],
                          name: str,
                          bussines_name: str,
                          zip_code: str,
                          city: str,
                          street: str,
                          building_number: int,
                          apartment_numer: int,
                          charge_value: Optional[int],
                          end_of_week_collection: Optional[bool]):
        if not self.token:
            raise NotAuthenticatedError

        raise NotImplementedError

    async def new_parcel(self):
        if not self.token:
            raise NotAuthenticatedError

        raise NotImplementedError
