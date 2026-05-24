# =========================================================
#                   MULTI COOKIE VERSION
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
from selenium.common.exceptions import TimeoutException

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
    return datetime.now(ist).strftime("%d-%m-%Y %I:%M:%S %p IST")


# =========================================================
#                   COOKIE SESSION
# =========================================================

class CookieSession:

    def __init__(self, cookie_id, cookie_str):

        self.cookie_id = cookie_id
        self.cookie_str = cookie_str

        self.driver = None
        self.wait = None

        self.active = False


# =========================================================
#                   MAIN CLASS
# =========================================================

class FacebookMessenger:

    def __init__(self):

        self.sessions = []

        self.target_uid = ""
        self.messages = []

        self.haters_name = ""
        self.delay = 10

        self.global_msg_index = 0

    # =====================================================
    #               SAFE WAIT FUNCTION
    # =====================================================

    def safe_wait(self, driver, condition, timeout=60):

        try:
            return WebDriverWait(
                driver,
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

            # =================================================
            #               LOAD MULTI COOKIES
            # =================================================

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

            if len(cookie_lines) > 5:
                raise Exception("MAXIMUM 5 COOKIES ALLOWED")

            for i, cookie in enumerate(cookie_lines, start=1):

                self.sessions.append(
                    CookieSession(i, cookie)
                )

            if len(self.sessions) == 0:
                raise Exception("NO COOKIES FOUND")

            # =================================================
            #                   OTHER FILES
            # =================================================

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

            if os.path.exists("hatersname.txt"):

                self.haters_name = open(
                    "hatersname.txt",
                    "r",
                    encoding="utf-8"
                ).read().strip()

            if os.path.exists("time.txt"):

                self.delay = int(
                    open("time.txt").read().strip()
                )

            if (
                not self.target_uid
                or not self.messages
            ):
                raise Exception("FILES EMPTY OR MISSING")

            success("ALL FILES AUTO-LOADED SUCCESSFULLY")

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
    #                   DRIVER SETUP
    # =====================================================

    def create_driver(self):

        options = Options()

        # =================================================
        #           HEADLESS + LOW MEMORY MODE
        # =================================================

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.page_load_strategy = "eager"

        # =================================================
        #               MEMORY OPTIMIZATION
        # =================================================

        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=128")
        options.add_argument("--disable-renderer-backgrounding")

        options.add_argument("--disable-images")

        options.add_argument(
            "--blink-settings=imagesEnabled=false"
        )

        # =================================================
        #               EXTRA PERFORMANCE
        # =================================================

        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")

        options.add_argument("--window-size=1280,720")

        # =================================================
        #               CHROME LOG REDUCTION
        # =================================================

        options.add_argument("--log-level=3")

        options.add_experimental_option(
            "excludeSwitches",
            ["enable-logging"]
        )

        # =================================================
        #               ISOLATED STORAGE
        # =================================================

        unique_profile = (
            f"/tmp/chrome_profile_{time.time_ns()}"
        )

        options.add_argument(
            f"--user-data-dir={unique_profile}"
        )

        service = Service("/usr/bin/chromedriver")

        driver = webdriver.Chrome(
            service=service,
            options=options
        )

        return driver

    # =====================================================
    #               LOGIN SINGLE SESSION
    # =====================================================

    def login_session(self, session):

        try:

            info(
                f"COOKIE {session.cookie_id} "
                f"STARTING DRIVER"
            )

            session.driver = self.create_driver()

            session.wait = WebDriverWait(
                session.driver,
                40
            )

            session.driver.get(
                "https://www.facebook.com"
            )

            self.safe_wait(
                session.driver,
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete",
                60
            )

            cookies = session.cookie_str.split(";")

            added = 0

            for cookie in cookies:

                if "=" in cookie:

                    name, value = cookie.strip().split(
                        "=",
                        1
                    )

                    try:

                        session.driver.add_cookie({
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

            # =================================================
            #               OPEN MESSENGER
            # =================================================

            session.driver.get(
                f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}"
            )

            loaded = self.safe_wait(
                session.driver,
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[@contenteditable='true']"
                    )
                ),
                60
            )

            if not loaded:
                raise Exception("CHAT OPEN FAILED")

            session.active = True

            success(
                f"COOKIE {session.cookie_id} "
                f"LOGIN SUCCESSFUL"
            )

            return True

        except Exception as e:

            error(
                f"COOKIE {session.cookie_id} "
                f"LOGIN FAILED : {e}"
            )

            return False

    # =====================================================
    #               SEND MESSAGE
    # =====================================================

    def send_message(self, session, text):

        try:

            driver = session.driver

            # =================================================
            #               PAGE READY
            # =================================================

            loaded = self.safe_wait(
                driver,
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete",
                120
            )

            if not loaded:
                raise Exception("PAGE LOAD TIMEOUT")

            # =================================================
            #               MESSAGE BOX
            # =================================================

            box = self.safe_wait(
                driver,
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[@contenteditable='true']"
                    )
                ),
                120
            )

            if not box:
                raise Exception("MESSAGE BOX NOT READY")

            # =================================================
            #               FOCUS
            # =================================================

            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center'
                });
                """,
                box
            )

            driver.execute_script(
                "arguments[0].focus();",
                box
            )

            # =================================================
            #               FINAL MESSAGE
            # =================================================

            final_msg = (
                f"{self.haters_name} {text}"
            ).strip()

            # =================================================
            #               CLEAR OLD
            # =================================================

            box.send_keys(
                Keys.CONTROL,
                "a"
            )

            box.send_keys(Keys.BACKSPACE)

            time.sleep(0.5)

            # =================================================
            #               TYPE
            # =================================================

            box.send_keys(final_msg)

            typed = self.safe_wait(
                driver,
                lambda d: final_msg in box.text,
                60
            )

            if not typed:
                raise Exception("MESSAGE TYPE FAILED")

            time.sleep(1)

            # =================================================
            #               SEND
            # =================================================

            box.send_keys(Keys.ENTER)

            send_complete = self.safe_wait(
                driver,
                lambda d: box.text.strip() == "",
                60
            )

            if not send_complete:
                raise Exception("SEND CONFIRM FAILED")

            time.sleep(2)

            return True

        except Exception as e:

            error(
                f"COOKIE {session.cookie_id} "
                f"SEND FAILED : {e}"
            )

            try:

                session.driver.refresh()

                self.safe_wait(
                    session.driver,
                    lambda d: d.execute_script(
                        "return document.readyState"
                    ) == "complete",
                    120
                )

            except:
                pass

            return False

    # =====================================================
    #               START ALL SESSIONS
    # =====================================================

    def start_sessions(self):

        active_count = 0

        for session in self.sessions:

            ok = self.login_session(session)

            if ok:
                active_count += 1

        if active_count == 0:

            error("NO ACTIVE COOKIES")

            return False

        success(
            f"ACTIVE COOKIES : {active_count}"
        )

        return True

    # =====================================================
    #                       START
    # =====================================================

    def start(self):

        clear_screen()

        info("LOADING CONFIGURATION")

        if not self.auto_load():
            return

        if not self.start_sessions():
            return

        success("MULTI COOKIE MESSAGE LOOP STARTED")

        count = 0

        while True:

            for session in self.sessions:

                if not session.active:
                    continue

                # =============================================
                # GLOBAL MESSAGE ROTATION
                # =============================================

                msg = self.messages[
                    self.global_msg_index
                ]

                self.global_msg_index += 1

                if self.global_msg_index >= len(self.messages):
                    self.global_msg_index = 0

                current_time = get_current_time()

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

                # =============================================
                # STABLE LOG
                # =============================================

                log(
                        f"[ALIVE] "
                        f"[MSG #{count}] "
                        f"[COOKIE: {session.cookie_id}] "
                        f"[TARGET: {self.target_uid}] "
                        f"[TIME: {current_time}] "
                        f"[STATUS: {status}] "
                        f"[MESSAGE: {short_msg}]"
                )

                log("───────────────────────────────────────────────────────────────")

                # =============================================
                # WAIT
                # =============================================

                for _ in range(self.delay):

                    time.sleep(1)

                    # =========================================
                    # DRIVER ALIVE CHECK
                    # =========================================

                    try:
                        session.driver.title

                    except:

                        error(
                            f"COOKIE {session.cookie_id} "
                            f"DRIVER CRASHED"
                        )

                        session.active = False

                        break


# =========================================================
#                       RUN SCRIPT
# =========================================================

if __name__ == "__main__":

    bot = FacebookMessenger()

    bot.start()