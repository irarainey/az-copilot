from azure.identity import AzureCliCredential
from azext_copilot.constants import AZURE_TOKEN_SCOPE


# This class is used to authenticate the user with Azure
class AuthenticationService:
    def __init__(self):
        # The AzureCliCredential class is used to authenticate the user with Azure
        self._credential = AzureCliCredential()

    def is_authenticated(self):
        try:
            # The get_token method is used to get the token from the token cache
            token = self._credential.get_token(AZURE_TOKEN_SCOPE)
            return token is not None
        except Exception:
            return False

    @property
    def credential(self):
        return self._credential
