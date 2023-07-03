from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential


class Credential(TokenCredential):
    def __init__(self, token):
        self.token = token
        # Hack to workaround autorest requiring the token to have an expires_on attribute.
        self.expires_on = 301

    def get_token(self, *scopes, **kwargs):
        return self


class AsyncCredential(AsyncTokenCredential):
    def __init__(self, token):
        self.token = token
        # Hack to workaround autorest requiring the token to have an expires_on attribute.
        self.expires_on = 301

    async def get_token(self, *scopes, **kwargs):
        return self
