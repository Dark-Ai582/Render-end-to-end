# =========================================================
#              SINGLE DRIVER MULTI COOKIE VERSION
# =========================================================

import os
import sys
import time
import logging

from datetime import datetime
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException
)

# =========================================================
#               RAILWAY REAL-TIME LOGGING FIX
# =========================================================

os.environ["PYTHONUNBUFFERED"] = "1"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

logger = logging.getLogger("railway")


def log(msg=""):
    logger.info(msg)


# =========================================================
#                   SIMPLE CLEAN LOGS
# =========================================================

def clear_screen():
    pass


def success(msg):
    log(f"[SUCCESS] {msg}")


def error(msg):
    log(f"[ERROR] {msg}")


def info(msg):
    log(f"[INFO] {msg}")


def get_current_time():

    ist = ZoneInfo("Asia/Kolkata")

    return datetime.now(ist).strftime(
        "%d-%m-%Y %I:%M:%S %p IST"
    )


# =========================================================
#                   COOKIE SESSION
# =========================================================

class CookieSession:

    def __init__(self, cookie_id, cookie_str):

        self.cookie_id = cookie_id
        self.cookie_str = cookie_str

        self.active = True


# =========================================================
#                   MAIN CLASS
# =========================================================

class FacebookMessenger:

    def __init__(self):

        self.sessions = []

        self.driver = None
        self.wait = None

        self.target_uid = ""
        self.messages = []

        self.haters_name = ""
        self.delay = 10

        self.global_msg_index = 0

    # =====================================================
    #                   SAFE WAIT
    # =====================================================

    def safe_wait(
        self,
        condition,
        timeout=60
    ):

        try:

            return WebDriverWait(
                self.driver,
                timeout,
                poll_frequency=0.5
            ).until(condition)

        except TimeoutException:
            return False

    # =====================================================
    #                   AUTO LOAD
    # =====================================================

    def auto_load(self):

        try:

            raw_cookies = open(
                "cookies.txt",
                "r",
                encoding="utf-8"
            ).read().strip()

            cookie_lines = [
                x.strip()
                for x in raw_cookies.splitlines()
                if x.strip()
            ]

            if len(cookie_lines) == 0:
                raise Exception("NO COOKIES FOUND")

            if len(cookie_lines) > 5:
                raise Exception("MAXIMUM 5 COOKIES ALLOWED")

            for i, cookie in enumerate(
                cookie_lines,
                start=1
            ):

                self.sessions.append(
                    CookieSession(i, cookie)
                )

            self.target_uid = open(
                "target_uid.txt",
                "r",
                encoding="utf-8"
            ).read().strip()

            self.messages = [
                x.strip()
                for x in open(
                    "messages.txt",
                    "r",
                    encoding="utf-8"
                )
                if x.strip()
            ]

            if os.path.exists(
                "hatersname.txt"
            ):

                self.haters_name = open(
                    "hatersname.txt",
                    "r",
                    encoding="utf-8"
                ).read().strip()

            if os.path.exists("time.txt"):

                self.delay = int(
                    open(
                        "time.txt"
                    ).read().strip()
                )

            if (
                not self.target_uid
                or not self.messages
            ):
                raise Exception(
                    "FILES EMPTY OR MISSING"
                )

            success(
                "ALL FILES AUTO-LOADED SUCCESSFULLY"
            )

            log(
                f"[CONFIG] "
                f"[TOTAL_COOKIES: {len(self.sessions)}] "
                f"[TARGET: {self.target_uid}] "
                f"[TOTAL_MSGS: {len(self.messages)}] "
                f"[DELAY: {self.delay}s]"
            )

            return True

        except Exception as e:

            error(f"AUTO LOAD FAILED : {e}")

            return False

    # =====================================================
    #                   CREATE DRIVER
    # =====================================================

    def create_driver(self):

        options = Options()

        # =================================================
        #               HEADLESS MODE
        # =================================================

        options.add_argument("--headless=new")

        # =================================================
        #               STABILITY
        # =================================================

        options.add_argument("--no-sandbox")

        options.add_argument(
            "--disable-dev-shm-usage"
        )

        options.add_argument("--disable-gpu")

        options.add_argument(
            "--disable-software-rasterizer"
        )

        options.add_argument("--no-zygote")

        options.add_argument("--single-process")

        options.add_argument(
            "--disable-features=site-per-process"
        )

        options.add_argument(
            "--disable-features=IsolateOrigins"
        )

        options.add_argument(
            "--disable-renderer-backgrounding"
        )

        options.add_argument(
            "--memory-pressure-off"
        )

        options.add_argument(
            "--max_old_space_size=128"
        )

        # =================================================
        #               SPEED
        # =================================================

        options.add_argument(
            "--blink-settings=imagesEnabled=false"
        )

        options.add_argument(
            "--disable-notifications"
        )

        options.add_argument(
            "--disable-popup-blocking"
        )

        options.add_argument(
            "--disable-extensions"
        )

        options.add_argument(
            "--disable-infobars"
        )

        options.add_argument(
            "--window-size=1280,720"
        )

        # =================================================
        #               LOG REDUCTION
        # =================================================

        options.add_argument("--log-level=3")

        options.add_experimental_option(
            "excludeSwitches",
            ["enable-logging"]
        )

        # =================================================
        #               PAGE LOAD
        # =================================================

        options.page_load_strategy = "eager"

        # =================================================
        #               UNIQUE PROFILE
        # =================================================

        unique_profile = (
            f"/tmp/chrome_{time.time_ns()}"
        )

        options.add_argument(
            f"--user-data-dir={unique_profile}"
        )

        service = Service(
            "/usr/bin/chromedriver"
        )

        self.driver = webdriver.Chrome(
            service=service,
            options=options
        )

        self.wait = WebDriverWait(
            self.driver,
            60
        )

        success("SINGLE DRIVER STARTED")

    # =====================================================
    #                   RESTART DRIVER
    # =====================================================

    def restart_driver(self):

        error("DRIVER CRASH DETECTED")

        try:
            self.driver.quit()
        except:
            pass

        self.driver = None
        self.wait = None

        time.sleep(3)

        self.create_driver()

    # =====================================================
    #                   CLEAR COOKIES
    # =====================================================

    def clear_browser(self):

        try:

            self.driver.delete_all_cookies()

            self.driver.execute_script("""
                window.localStorage.clear();
                window.sessionStorage.clear();
            """)

        except:
            pass

    # =====================================================
    #                   SWITCH COOKIE
    # =====================================================

    def switch_cookie(
        self,
        session
    ):

        try:

            info(
                f"SWITCHING TO COOKIE "
                f"{session.cookie_id}"
            )

            self.driver.get(
                "https://www.facebook.com"
            )

            loaded = self.safe_wait(
                lambda d:
                d.execute_script(
                    "return document.readyState"
                ) == "complete",
                60
            )

            if not loaded:
                raise Exception(
                    "FACEBOOK LOAD FAILED"
                )

            # =============================================
            # CLEAR OLD COOKIE DATA
            # =============================================

            self.clear_browser()

            # =============================================
            # ADD NEW COOKIES
            # =============================================

            cookies = session.cookie_str.split(";")

            added = 0

            for cookie in cookies:

                if "=" in cookie:

                    name, value = cookie.strip().split(
                        "=",
                        1
                    )

                    try:

                        self.driver.add_cookie({
                            "name": name,
                            "value": value,
                            "domain": ".facebook.com"
                        })

                        added += 1

                    except:
                        pass

            success(
                f"COOKIE {session.cookie_id} "
                f"LOADED : {added}"
            )

            # =============================================
            # OPEN CHAT
            # =============================================

            self.driver.get(
                f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}"
            )

            box = self.safe_wait(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[@contenteditable='true']"
                    )
                ),
                60
            )

            if not box:
                raise Exception(
                    "CHAT OPEN FAILED"
                )

            success(
                f"COOKIE {session.cookie_id} "
                f"READY"
            )

            return True

        except Exception as e:

            error(
                f"COOKIE {session.cookie_id} "
                f"SWITCH FAILED : {e}"
            )

            return False

    # =====================================================
    #                   SEND MESSAGE
    # =====================================================

    def send_message(
        self,
        session,
        text
    ):

        try:

            # =============================================
            # DRIVER ALIVE CHECK
            # =============================================

            try:
                self.driver.title
            except:
                self.restart_driver()

            # =============================================
            # SWITCH COOKIE
            # =============================================

            switched = self.switch_cookie(
                session
            )

            if not switched:
                return False

            # =============================================
            # WAIT PAGE READY
            # =============================================

            loaded = self.safe_wait(
                lambda d:
                d.execute_script(
                    "return document.readyState"
                ) == "complete",
                120
            )

            if not loaded:
                raise Exception(
                    "PAGE LOAD TIMEOUT"
                )

            # =============================================
            # MESSAGE BOX
            # =============================================

            box = self.safe_wait(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[@contenteditable='true']"
                    )
                ),
                120
            )

            if not box:
                raise Exception(
                    "MESSAGE BOX NOT READY"
                )

            # =============================================
            # FOCUS
            # =============================================

            self.driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center'
                });
                """,
                box
            )

            self.driver.execute_script(
                "arguments[0].focus();",
                box
            )

            # =============================================
            # FINAL MESSAGE
            # =============================================

            final_msg = (
                f"{self.haters_name} {text}"
            ).strip()

            # =============================================
            # CLEAR OLD
            # =============================================

            box.send_keys(
                Keys.CONTROL,
                "a"
            )

            box.send_keys(
                Keys.BACKSPACE
            )

            time.sleep(0.5)

            # =============================================
            # TYPE MESSAGE
            # =============================================

            box.send_keys(final_msg)

            typed = self.safe_wait(
                lambda d:
                final_msg in box.text,
                60
            )

            if not typed:
                raise Exception(
                    "MESSAGE TYPE FAILED"
                )

            time.sleep(1)

            # =============================================
            # SEND MESSAGE
            # =============================================

            box.send_keys(Keys.ENTER)

            send_complete = self.safe_wait(
                lambda d:
                box.text.strip() == "",
                60
            )

            if not send_complete:
                raise Exception(
                    "SEND CONFIRM FAILED"
                )

            time.sleep(2)

            return True

        except Exception as e:

            error(
                f"COOKIE {session.cookie_id} "
                f"SEND FAILED : {e}"
            )

            return False

    # =====================================================
    #                   START
    # =====================================================

    def start(self):

        clear_screen()

        info("LOADING CONFIGURATION")

        if not self.auto_load():
            return

        self.create_driver()

        success(
            "SINGLE DRIVER MULTI COOKIE LOOP STARTED"
        )

        count = 0

        while True:

            for session in self.sessions:

                if not session.active:
                    continue

                try:

                    msg = self.messages[
                        self.global_msg_index
                    ]

                    self.global_msg_index += 1

                    if (
                        self.global_msg_index
                        >= len(self.messages)
                    ):
                        self.global_msg_index = 0

                    current_time = (
                        get_current_time()
                    )

                    sent = self.send_message(
                        session,
                        msg
                    )

                    count += 1

                    short_msg = (
                        msg[:60] + "..."
                        if len(msg) > 60
                        else msg
                    )

                    status = (
                        "SUCCESS"
                        if sent
                        else "FAILED"
                    )

                    log(
                        f"[ALIVE] "
                        f"[MSG #{count}] "
                        f"[COOKIE: {session.cookie_id}] "
                        f"[TARGET: {self.target_uid}] "
                        f"[TIME: {current_time}] "
                        f"[STATUS: {status}] "
                        f"[MESSAGE: {short_msg}]"
                    )

                    log(
                        "────────────────────────────────────────────"
                    )

                    # =====================================
                    # WAIT
                    # =====================================

                    for _ in range(
                        self.delay
                    ):

                        time.sleep(1)

                        try:
                            self.driver.title

                        except:

                            self.restart_driver()

                            break

                except WebDriverException:

                    self.restart_driver()

                except Exception as e:

                    error(
                        f"MAIN LOOP ERROR : {e}"
                    )

                    time.sleep(5)


# =========================================================
#                       RUN
# =========================================================

if __name__ == "__main__":

    bot = FacebookMessenger()

    bot.start()