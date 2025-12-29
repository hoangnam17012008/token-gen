import requests
from typing import Tuple, Optional
from Core.communication.mail.base import MailApi


class KanashiApi(MailApi):
    BASE_URL = "https://mailapi.kanashi.xyz"

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def create_account(self, username: str, password: str) -> Optional[Tuple[str, str]]:
        try:
            resp = requests.post(
                f"{self.BASE_URL}/create_inbox",
                json={"api_key": self.api_key},
                timeout=15,
            )

            if not resp.ok:
                return None

            data = resp.json()
            if data.get("status") != "success":
                return None

            inbox_data = data.get("data", {})
            email = inbox_data.get("address")
            token = inbox_data.get("token")

            if email and token:
                # Return email and token (as password)
                return email, token

            return None
        except Exception:
            return None

    def fetch_inbox(self, email: str, password: str) -> list:
        # Use password as token
        token = password

        try:
            resp = requests.post(
                f"{self.BASE_URL}/get_emails",
                json={
                    "api_key": self.api_key,
                    "inbox_id": email,
                    "inbox_token": token,
                },
                timeout=15,
            )

            if not resp.ok:
                return []

            data = resp.json()
            if data.get("status") == "success":
                return data.get("data", [])

            return []
        except Exception:
            return []
