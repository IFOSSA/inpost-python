from aiohttp import ClientSession


class Inpost():
    def __init__(self):
        self.url: str = ...
        self.token: str = ...
        self.auth = ...
        self.username: str = ...
        self.password: str = ...
        self.sess: ClientSession = ...
        ...

    def __repr__(self):
        ...

    async def get(self):
        yield self.sess.get()

    async def post(self):
        yield self.sess.post()

    async def authenticated(self):
        ...
