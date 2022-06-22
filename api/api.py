from aiohttp import ClientSession
from json import dumps
from static.endpoints import login
from static.headers import appjson
from static.exceptions import NotAuthenticatedError, NotImplementedError


class Inpost:
    def __init__(self, uname: str, passwd: str):
        self.username: str = uname
        self.password: str = passwd
        self.token: str | None = None
        self.auth: bool | None = None
        self.sess: ClientSession = ClientSession()

    def __repr__(self):
        return f'Username: {self.username}\nPassword: {self.password}\nToken: {self.token}'

    async def authenticate(self):
        resp = await self.sess.post(url=login,
                                    headers=appjson,
                                    data=dumps({'login': self.username,
                                                'password': self.password}))
        if resp.status == 200:
            self.auth = True
            token = await resp.json()
            self.token = token['token']
        else:
            raise NotAuthenticatedError(await resp.text())

    async def disconnect(self):
        await self.sess.close()

    async def my_parcels(self):
        if not self.auth:
            raise NotAuthenticatedError

        raise NotImplementedError

    async def send_parcel(self):
        if not self.auth:
            raise NotAuthenticatedError

        raise NotImplementedError

    async def new_parcel(self):
        if not self.auth:
            raise NotAuthenticatedError

        raise NotImplementedError
