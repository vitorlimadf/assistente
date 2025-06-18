import os
import msal
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

class TokenManager:
    def __init__(self, cache_path="token_cache.json"):
        self.client_id = os.getenv("CLIENT_ID")
        self.tenant_id = os.getenv("TENANT_ID")
        self.scope = ["Mail.Read", "Contacts.ReadWrite","Tasks.Read"]
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        #self.scope = ["https://graph.microsoft.com/.default"]

        # Cache persistente
        self.cache_path = cache_path
        self.token_cache = msal.SerializableTokenCache()

        if os.path.exists(self.cache_path):
            self.token_cache.deserialize(open(self.cache_path, "r").read())

        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            token_cache=self.token_cache
        )

    def persist_cache(self):
        if self.token_cache.has_state_changed:
            with open(self.cache_path, "w") as f:
                f.write(self.token_cache.serialize())

    def get_access_token(self):
        accounts = self.app.get_accounts()
        result = None

        if accounts:
            result = self.app.acquire_token_silent(self.scope, account=accounts[0])

        if not result:
            result = self.app.acquire_token_interactive(
                scopes=self.scope,
                prompt="consent"
            )


        if "access_token" in result:
            self.persist_cache()
            return result["access_token"]

        raise RuntimeError(f"Erro ao obter token: {result.get('error_description')}")
