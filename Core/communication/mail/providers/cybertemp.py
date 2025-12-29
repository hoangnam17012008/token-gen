import random
import requests

from typing import Optional, List
from Core.communication.mail.base import MailApi


class CybertempApi(MailApi):
    BASE_URL = "https://api.cybertemp.xyz"
    DOMAINS = ["emziegz.com", "loganister.com", "resolutux.com", "rexabot.com"]

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.api_key = api_key

    def create_account(self, username: str, password: str) -> Optional[tuple[str, str]]:
        email = f"{username}@{random.choice(self.DOMAINS)}"

        try:
            self.fetch_inbox(email, password)
        except Exception as e:
            raise RuntimeError(
                f"CyberTemp inbox validation failed for {email} -> {e}"
            ) from e

        return email, password

    def fetch_inbox(self, email: str, password: str = None) -> List[dict]:
        try:
            resp = requests.get(
                f"{self.BASE_URL}/getMail",
                params={"email": email},
                headers=self.headers,
                timeout=15,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Network error fetching CyberTemp inbox: {e}")

        if not resp.ok:
            raise RuntimeError(
                f"CyberTemp API returned {resp.status_code}: {resp.text}"
            )

        data = resp.json()
        messages = data.get("emails", []) if isinstance(data, dict) else data

        normalized = []
        for msg in messages:
            normalized.append(
                {
                    "id": msg.get("id"),
                    "from": msg.get("from"),
                    "to": msg.get("to"),
                    "subject": msg.get("subject"),
                    "body": msg.get("body") or msg.get("text") or "",
                    "html": msg.get("html", ""),
                }
            )
        return normalized

    def delete_mailbox(self, email: str) -> bool:
        try:
            resp = requests.delete(
                f"https://www.cybertemp.xyz/api/user/inboxes/{email}",
                headers=self.headers,
                timeout=10,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to delete mailbox: {e}")

        if resp.ok:
            return True
        else:
            raise RuntimeError(
                f"Failed to delete mailbox: {resp.status_code} {resp.text}"
            )
