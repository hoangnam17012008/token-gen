import requests
from Core.communication.mail.base import MailApi


class KatMailApi(MailApi):
    BASE_URL = "http://103.114.203.91:8080/api"
    DOMAIN = "tempmail.katxd.xyz"

    def create_account(self, username: str, password: str):
        email = f"{username}@{self.DOMAIN}"

        resp = requests.post(
            f"{self.BASE_URL}/create_account",
            json={"email": email, "password": password},
            headers=self.headers,
            timeout=15,
        )

        if not resp.ok:
            raise RuntimeError("KatMail account creation failed")

        return email, password

    def fetch_inbox(self, email: str, password: str):
        resp = requests.post(
            f"{self.BASE_URL}/get_inbox",
            json={"email": email, "password": password},
            headers=self.headers,
            timeout=15,
        )

        if not resp.ok:
            raise RuntimeError("KatMail inbox fetch failed")

        return resp.json()
