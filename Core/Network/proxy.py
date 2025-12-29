from threading import Lock


class ProxyProvider:
    def __init__(self, file: str):
        self.file = file
        self.lock = Lock()

    def get(self) -> str | None:
        with self.lock:
            try:
                with open(self.file, "r+", encoding="utf-8") as f:
                    proxies = [p.strip() for p in f if p.strip()]

                    if not proxies:
                        return None

                    proxy = proxies.pop(0)

                    if not any(
                        proxy.startswith(p)
                        for p in ["http://", "https://", "socks4://", "socks5://"]
                    ):
                        proxy = f"http://{proxy}"

                    f.seek(0)
                    f.truncate()
                    f.write("\n".join(proxies))

                    return proxy
            except FileNotFoundError:
                return None
