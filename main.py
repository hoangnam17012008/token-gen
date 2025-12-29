import json
import os
import time
import threading

from Core.Flow.generator import TokenGenerator
from Core.Network.proxy import ProxyProvider
from Core.accounts.factory import AccountContextFactory
from Core.accounts.storage import TokenStorage
from Core.accounts.context import TitleBarStats
from Core.utils.titlebar import TitleBarUpdater
from Core.discord.register import DiscordRegisterService
from Core.discord.session import DiscordSessionFactory
from Core.communication.mail.factory import MailApiFactory
from Core.communication.mail.verify import MailVerify
from Core.Flow.solver import Solver
from Core.logging.logger import VatosLogger
from Core.utils.humaniser import Humaniser
from Core.NexusColors.color import NexusColor

proxy_lock = threading.Lock()

def worker(proxy_provider, config, stats):
    with proxy_lock:
        proxy = proxy_provider.get()

    if not proxy:
        print("No proxies available")
        return

    session = DiscordSessionFactory(proxy).create()
    logger = VatosLogger(config)
    mail_api = MailApiFactory(config).create()

    generator = TokenGenerator(
        context_factory=AccountContextFactory(session, proxy, logger, mail_api),
        register=DiscordRegisterService(session, logger, stats),
        captcha=Solver(logger, config),
        email_verifier=MailVerify(session, logger, stats),
        storage=TokenStorage(),
        humaniser=Humaniser(config, session, logger),
        logger=logger,
        config=config,
        mail_api=mail_api,
        stats=stats
    )

    generator.run()


def main():
    config = json.load(open("config.json", encoding="utf-8"))

    stats = TitleBarStats()
    titlebar = TitleBarUpdater(stats.format_title, interval=0.1)
    titlebar.start()

    print(f"""{NexusColor.PURPLE}
            ██████╗ ██████╗ ██████╗ 
            ╚════██╗╚════██╗╚════██╗
            ▄███╔╝  ▄███╔╝  ▄███╔╝
            ▀▀══╝   ▀▀══╝   ▀▀══╝ 
            ██╗     ██╗     ██╗   
            ╚═╝     ╚═╝     ╚═╝ 
            """)

    proxy_provider = ProxyProvider("io/input/proxies.txt")
    threads_count = int(config.get("threads", 1))

    while True:
        threads = []

        for i in range(threads_count):
            t = threading.Thread(
                target=worker,
                args=(proxy_provider, config, stats),
                daemon=True
            )
            t.start()
            threads.append(t)

            time.sleep(10)

        for t in threads:
            t.join()


if __name__ == "__main__":
    os.system("cls")
    main()
