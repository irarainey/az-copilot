from azure.identity import AzureCliCredential


class AuthenticationService:
    def __init__(self):
        self._credential = AzureCliCredential()

    def is_authenticated(self):
        try:
            token = self._credential.get_token("https://management.azure.com/.default")
            return token is not None
        except Exception as e:
            print(e)
            return False

    @property
    def credential(self):
        return self._credential
