import asyncio
import threading
import random
import string
import time

from flask import Flask, request
from ..captcha.solver import HCaptchaSolver
from ..captcha.storage import TaskStore


class APIServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.store = TaskStore()
        self.solver = HCaptchaSolver(self.store)

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        self._routes()

    def _routes(self):
        @self.app.route("/solve")
        def solve():
            taskid = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=5)
            )
            self.store.create(taskid)

            asyncio.run_coroutine_threadsafe(
                self.solver.solve(
                    taskid=taskid,
                    url=request.args["url"],
                    sitekey=request.args["sitekey"],
                    rqdata=request.args.get("rqdata"),
                    proxy=request.args.get("proxy"),
                ),
                self.loop,
            )
            return {"taskid": taskid}

        @self.app.route("/task/<taskid>")
        def task(taskid):
            return self.store.get(taskid)

    def run(self):
        self.app.run("0.0.0.0", 6946, debug=False, use_reloader=False)
