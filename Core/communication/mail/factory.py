from Core.communication.mail.providers.katmail import KatMailApi
from Core.communication.mail.providers.cybertemp import CybertempApi
from Core.communication.mail.providers.kanashi import KanashiApi


class MailApiFactory:
    def __init__(self, config: dict):
        self.api_key = config["verification"]["mail_api_key"]
        self.provider = config["verification"]["mail_provider"]

    def create(self):
        if not self.api_key:
            raise ValueError("No API Key")

        if not self.provider:
            raise ValueError("No Mail Provider")

        if self.provider == "katmail":
            return KatMailApi(self.api_key)

        if self.provider == "cybertemp":
            return CybertempApi(self.api_key)

        if self.provider == "kanashi":
            return KanashiApi(self.api_key)

        raise ValueError(f"Unknown mail provider: {self.provider}")
