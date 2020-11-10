import logging
import random
import string
import requests

# Import Detection From Stealth
from .get_acrawler import get_acrawler
from playwright import sync_playwright

try:
    playwright = sync_playwright().start()
except Exception as e:
    raise e

async_support = False

logger = logging.getLogger(__name__)


def get_playwright():
    return playwright


class browser:
    def __init__(
        self,
        **kwargs,
    ):
        self.debug = kwargs.get("debug", False)
        self.proxy = kwargs.get("proxy", None)
        self.api_url = kwargs.get("api_url", None)
        self.referrer = kwargs.get("referer", "https://www.tiktok.com/")
        self.language = kwargs.get("language", "en")
        self.executablePath = kwargs.get("executablePath", None)
        self.did = kwargs.get("custom_did", None)

        args = kwargs.get("browser_args", [])
        options = kwargs.get("browser_options", {})

        self.userAgent = (  # TODO: used?
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.111 Safari/537.36"
        )

        if len(args) == 0:
            self.args = []
        else:
            self.args = args

        self.options = {
            "headless": True,
            "handleSIGINT": True,
            "handleSIGTERM": True,
            "handleSIGHUP": True,
        }

        if self.proxy is not None:
            if "@" in self.proxy:
                server_prefix = self.proxy.split("://")[0]
                address = self.proxy.split("@")[1]
                self.options["proxy"] = {
                    "server": server_prefix + "://" + address,
                    "username": self.proxy.split("://")[1].split(":")[0],
                    "password": self.proxy.split("://")[1].split("@")[0].split(":")[1],
                }
            else:
                self.options["proxy"] = {"server": self.proxy}

        self.options.update(options)

        if self.executablePath is not None:
            self.options["executablePath"] = self.executablePath

        try:
            self.browser = playwright.webkit.launch(args=self.args, **self.options)
        except Exception as exc:
            logging.critical(exc)
            raise

        page = self.create_page(set_useragent=True)
        self.get_params(page)
        page.close()

    def get_params(self, page) -> None:
        self.browser_language = ""
        self.timezone_name = ""
        self.browser_platform = ""
        self.browser_name = ""
        self.browser_version = ""
        """
        self.browser_language = await self.page.evaluate(
            "() => { return navigator.language || navigator.userLanguage; }"
        )
        self.timezone_name = await self.page.evaluate(
            "() => { return Intl.DateTimeFormat().resolvedOptions().timeZone; }"
        )
        self.browser_platform = await self.page.evaluate(
            "() => { return window.navigator.platform; }"
        )
        self.browser_name = await self.page.evaluate(
            "() => { return window.navigator.appCodeName; }"
        )
        self.browser_version = await self.page.evaluate(
            "() => { return window.navigator.appVersion; }"
        )
        """

        self.width = page.evaluate("""() => { return screen.width; }""")
        self.height = page.evaluate("""() => { return screen.height; }""")

    def create_page(self, set_useragent=False):
        iphone = playwright.devices["iPhone 11 Pro"]
        iphone["viewport"] = {
            "width": random.randint(320, 1920),
            "height": random.randint(320, 1920),
        }
        iphone["deviceScaleFactor"] = random.randint(1, 3)
        iphone["isMobile"] = random.randint(1, 2) == 1
        iphone["hasTouch"] = random.randint(1, 2) == 1

        context = self.browser.newContext(**iphone)
        if set_useragent:
            self.userAgent = iphone["userAgent"]
        page = context.newPage()

        return page

    def sign_url(self, **kwargs):
        url = kwargs.get("url", None)
        if url is None:
            raise Exception("sign_url required a url parameter")
        page = self.create_page()
        verifyFp = "".join(
            random.choice(
                string.ascii_lowercase + string.ascii_uppercase + string.digits
            )
            for i in range(16)
        )

        if kwargs.get("custom_did", None) is not None:
            did = kwargs.get("custom_did", None)
        elif self.did is None:
            did = str(random.randint(10000, 999999999))
        else:
            did = self.did

        page.setContent("<script> " + get_acrawler() + " </script>")
        page_result = page.evaluate(
            '() => {'
            f' var url = "{url}&verifyFp={verifyFp}&did={did}";'
            '  var token = window.byted_acrawler.sign({url: url});'
            '  return token;'
            '}'
        )
        page.close()
        return (verifyFp, did, page_result)

    def clean_up(self):
        try:
            self.browser.close()
        except Exception:
            logging.info("cleanup failed")
        # playwright.stop()

    def find_redirect(self, url):
        self.page.goto(url, {"waitUntil": "load"})
        self.redirect_url = self.page.url

    def __format_proxy(self, proxy):
        if proxy is not None:
            return {"http": proxy, "https": proxy}
        else:
            return None

    def __get_js(self):
        return requests.get(
            "https://sf16-muse-va.ibytedtos.com/obj/rc-web-sdk-gcs/acrawler.js",
            proxies=self.__format_proxy(self.proxy),
        ).text
