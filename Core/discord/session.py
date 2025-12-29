import curl_cffi


class DiscordSessionFactory:
    def __init__(self, proxy: str | None):
        self.proxy = proxy

    def create(self):
        session = curl_cffi.Session(impersonate="chrome")

        if self.proxy:
            session.proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }

        return session
