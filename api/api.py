from typing import Optional, Union

import aiohttp.web
from aiohttp import ClientSession
from static.endpoints import logout, send_sms_code, confirm_sms_code
from static.headers import appjson
from static.exceptions import NotAuthenticatedError, NotImplementedError, SomeAPIError, PhoneNumberError, \
    SmsCodeConfirmationError
from static.parcels import ParcelDeliveryType, ParcelCarrierSize, ParcelLockerSize, ParcelShipmentType


class Inpost:
    def __init__(self, phone_number: str):
        self.phone_number: str = phone_number
        self.sms_code: str | None = None
        self.token: str | None = None
        self.sess: ClientSession = ClientSession()

    def __repr__(self):
        return f'Username: {self.phone_number}\nToken: {self.token}'

    async def send_sms_code(self) -> Optional[bool]:
        async with await self.sess.post(url=send_sms_code,
                                        json={
                                            'phoneNumber': f'{self.phone_number}'
                                        }) as phone:
            if phone.status == aiohttp.web.HTTPOk:
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
            if confirmation.status == aiohttp.web.HTTPOk:
                self.sms_code = sms_code
            else:
                raise SmsCodeConfirmationError(reason=confirmation)

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

    # async def get_parcels(self,
    #                       sender: Optional[str],
    #                       customer_reference: Optional[str],
    #                       parcel_code: Optional[Union[List[str], str]],
    #                       service_name: Union[List[ParcelServiceName], ParcelServiceName],
    #                       status: Optional[Union[List[str], str]],
    #                       date_from: str,
    #                       date_to: str,
    #                       end_of_week_collection: Optional[bool],
    #                       parcel_type: ParcelForm = ParcelForm.INCOMING,
    #                       limit=20,
    #                       page=1):
    #     if not self.token:
    #         raise NotAuthenticatedError
    #     temp_par = [
    #         '[packType{eq}%s]' % parcel_type.name.lower(),
    #         '[serviceMane{in}%s]' % ','.join((x.name for x in service_name)),
    #         '[dateFrom{eq}%s]' % date_from,
    #         '[dateTo{eq}%s]' % date_to
    #         ]
    #     async with await self.sess.get(url=get_parcels,
    #                                    headers={'X-Authorization': f'Bearer {self.token}'},
    #                                    params={
    #                                         'page': page,
    #                                         'limit': limit,
    #                                         'filters': ','.join(temp_par)
    #                                    }) as resp:
    #
    #     raise NotImplementedError

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
