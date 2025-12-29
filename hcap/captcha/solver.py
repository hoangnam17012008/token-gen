import asyncio
import time
import json

from ..captcha.browser import BrowserFactory
from ..web.templates import TemplateCache
from ..captcha.ai import AIAssistant


class HCaptchaSolver:
    def __init__(self, store):
        self.store = store
        self.templates = TemplateCache()
        self.config = json.load(open("config.json", encoding="utf-8"))

        # Load AI settings
        self.api_key = self.config["solver"]["ai_api_key"]
        self.service = self.config["solver"].get("ai_service", "openrouter")
        if not self.api_key:
            raise RuntimeError("No AI API Key")
        self.ai = AIAssistant(self.api_key, self.service)

    async def solve_accessibility_hcaptcha(self, frame):
        try:
            await frame.wait_for_selector("#menu-info", timeout=10_000)
            await frame.locator("#menu-info").click()
            await asyncio.sleep(0.3)

            try:
                await frame.locator("#text_challenge").click()
            except Exception:
                pass

            start_time = time.time()
            last_question = None

            while True:
                if frame.is_detached():
                    return time.time() - start_time

                try:
                    question_el = await frame.query_selector('[id^="prompt-text"]')
                    if not question_el:
                        await asyncio.sleep(0.2)
                        continue

                    question = (await question_el.inner_text()).strip()
                    if not question or question == last_question:
                        await asyncio.sleep(0.2)
                        continue

                    last_question = question

                    answer = await self.ai.answer(question)
                    answer = answer.lower().replace(".", "").strip()
                    if "ja" in answer or "yes" in answer:
                        answer = "ja"
                    else:
                        answer = "nee"

                    input_el = await frame.query_selector("div.challenge-input input")
                    if not input_el:
                        continue

                    await input_el.fill(answer)
                    await asyncio.sleep(0.2)

                    submit = await frame.query_selector(".button-submit")
                    if submit:
                        await submit.click()

                except Exception:
                    break

            return time.time() - start_time

        except Exception as e:
            print(f"Error solving accessibility hcaptcha: {e}")
            return 0.0

    async def _monitor_token(self, page, context, browser, taskid):
        while True:
            if page.is_closed():
                return

            try:
                token = await page.evaluate(
                    """() => document.querySelector(
                        "iframe[data-hcaptcha-response]"
                    )?.getAttribute("data-hcaptcha-response")"""
                )

                if token and "_" in token:
                    cookies = await context.cookies()
                    self.store.set_result(
                        taskid,
                        "success",
                        token,
                        {c["name"]: c["value"] for c in cookies},
                    )
                    await browser.close()
                    return

            except Exception:
                return

            await asyncio.sleep(0.5)

    async def solve(self, taskid, url, sitekey, rqdata, proxy):
        start = time.time()
        browser = None

        try:
            browser, context, page = await BrowserFactory.create(proxy)

            async def route_main(route):
                await route.fulfill(
                    body=self.templates.render_main(sitekey, rqdata),
                    content_type="text/html",
                )

            async def route_hcaptcha(route):
                await route.fulfill(
                    body=self.templates.render_hcaptcha(rqdata),
                    content_type="text/html",
                )

            async def route_api(route):
                await route.fulfill(
                    body=self.templates.api_js,
                    content_type="application/javascript",
                )

            await page.route(url, route_main)
            await page.route("**/static/hcaptcha.html", route_hcaptcha)
            await page.route("**/api.js", route_api)

            await page.goto(url, wait_until="commit")
            await page.wait_for_selector("iframe")

            token_task = asyncio.create_task(
                self._monitor_token(page, context, browser, taskid)
            )

            frame = await self.find_hcaptcha_frame(page)
            if not frame:
                raise RuntimeError("hCaptcha frame not found")

            print("[+] hCaptcha frame found")
            await self.solve_accessibility_hcaptcha(frame)

            await asyncio.wait_for(token_task, timeout=120)

        except asyncio.TimeoutError:
            self.store.set_result(taskid, "error")

        except Exception as e:
            print("Solve error:", e)
            self.store.set_result(taskid, "error")

        finally:
            if browser:
                await browser.close()

        return time.time() - start
