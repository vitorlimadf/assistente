import os
import requests
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self):
        self.tenant_id = os.getenv("TENANT_ID")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.refresh_token = os.getenv("REFRESH_TOKEN")  # opcional, se quiser carregar no boot
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.access_token = None
        self.expires_at = None

    def get_access_token(self):
        if self.access_token and datetime.utcnow() < self.expires_at:
            return self.access_token
        elif self.refresh_token:
            return self.refresh_access_token()
        else:
            raise RuntimeError("⚠️ Token expirado e nenhum refresh_token disponível.")

    def refresh_access_token(self):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default"
        }

        response = requests.post(self.token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            self.expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
            return self.access_token
        else:
            raise RuntimeError(f"Erro ao renovar token: {response.status_code} - {response.text}")
