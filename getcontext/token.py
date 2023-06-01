from azure.core.credentials import TokenCredential


class Credential(TokenCredential):
    def __init__(self, token):
        self.token = token

    def get_token(self, *scopes, **kwargs):
        return self
