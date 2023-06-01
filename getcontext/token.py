from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential


class Credential(TokenCredential):
    def __init__(self, token):
        self.token = token

    def get_token(self, *scopes, **kwargs):
        return self


class AsyncCredential(AsyncTokenCredential):
    def __init__(self, token):
        self.token = token

    async def get_token(self, *scopes, **kwargs):
        return self
