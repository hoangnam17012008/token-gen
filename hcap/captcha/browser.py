import re

from camoufox.async_api import AsyncCamoufox


class BrowserFactory:
    @staticmethod
    async def create(proxy=None):
        cfg = {
            "headless": True,
            "humanize": False,
            "block_webrtc": True,
            "geoip": True,
            "os": "windows",
        }
        if proxy:
            if "://" in proxy:
                proxy = proxy.split("://", 1)[1]

            user, password, server = re.match(r"(.*?):(.*?)@(.*)", proxy).groups()
            proxy_config = {"server": f"http://{server}"}
            proxy_config["username"] = user
            proxy_config["password"] = password
            cfg["proxy"] = proxy_config

        browser = await AsyncCamoufox(**cfg).start()
        context = await browser.new_context(locale="nl")
        page = await context.new_page()
        return browser, context, page
