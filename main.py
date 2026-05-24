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
    StaleElementReferenceException,
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
    return datetime.now(ist).strftime("%d-%m-%Y %I:%M:%S %p IST")


# =========================================================
#                   MAIN CLASS
# =========================================================

class FacebookMessenger:

    def __init__(self):

        self.driver = None
        self.wait = None

        self.cookie_str = ""
        self.target_uid = ""
        self.messages = []

        self.haters_name = ""

        # =================================================
        #               DEFAULT STABLE DELAY
        # =================================================

        self.delay = 20

    # =====================================================
    #                   AUTO LOAD
    # =====================================================

    def auto_load(self):

        try:

            self.cookie_str = open(
                "cookies.txt",
                "r",
                encoding="utf-8"
            ).read().strip()

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
                    open(
                        "time.txt",
                        "r",
                        encoding="utf-8"
                    ).read().strip()
                )

            if (
                not self.cookie_str
                or not self.target_uid
                or not self.messages
            ):
                raise Exception("FILES EMPTY OR MISSING")

            success("ALL FILES AUTO-LOADED SUCCESSFULLY")

            log(
                f"[CONFIG] "
                f"[TARGET: {self.target_uid}] "
                f"[TOTAL_MSGS: {len(self.messages)}] "
                f"[DELAY: {self.delay}s]"
            )

            return True

        except Exception as e:

            error(f"AUTO LOAD FAILED : {e}")

            return False

    # =====================================================
    #               WAIT UNTIL PAGE READY
    # =====================================================

    def wait_for_page_ready(self, timeout=60):

        try:

            WebDriverWait(
                self.driver,
                timeout
            ).until(
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete"
            )

            return True

        except:
            return False

    # =====================================================
    #                   DRIVER SETUP
    # =====================================================

    def setup_driver(self):

        try:

            options = Options()

            # =================================================
            #           HEADLESS + LOW MEMORY MODE
            # =================================================

            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")

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

            # =================================================
            #               STABILITY FIXES
            # =================================================

            options.add_argument("--disable-features=RendererCodeIntegrity")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-hang-monitor")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-translate")
            options.add_argument("--disable-features=site-per-process")
            options.add_argument("--renderer-process-limit=1")
            options.add_argument("--single-process")

            options.add_argument("--window-size=1280,720")

            # =================================================
            #               CHROME LOG REDUCTION
            # =================================================

            options.add_argument("--log-level=3")

            options.add_experimental_option(
                "excludeSwitches",
                ["enable-logging"]
            )

            service = Service("/usr/bin/chromedriver")

            self.driver = webdriver.Chrome(
                service=service,
                options=options
            )

            self.wait = WebDriverWait(
                self.driver,
                60
            )

            success("CHROME DRIVER STARTED")
            success("LOW MEMORY MODE ENABLED")
            success("RAILWAY LOGGING FIX ENABLED")

            return True

        except Exception as e:

            error(f"DRIVER ERROR : {e}")

            return False

    # =====================================================
    #               LOGIN USING COOKIES
    # =====================================================

    def login_with_cookies(self):

        try:

            info("OPENING FACEBOOK")

            self.driver.get(
                "https://www.facebook.com"
            )

            self.wait_for_page_ready(60)

            cookies = self.cookie_str.split(";")

            added = 0

            for cookie in cookies:

                if "=" in cookie:

                    name, value = cookie.strip().split(
                        "=",
                        1
                    )

                    self.driver.add_cookie({
                        "name": name,
                        "value": value,
                        "domain": ".facebook.com"
                    })

                    added += 1

            success(f"COOKIES LOADED : {added}")

            self.driver.get(
                "https://www.facebook.com/messages"
            )

            self.wait_for_page_ready(60)

            self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.TAG_NAME,
                        "body"
                    )
                )
            )

            success("LOGIN SUCCESSFUL")

            return True

        except Exception as e:

            error(f"COOKIE LOGIN FAILED : {e}")

            return False

    # =====================================================
    #               OPEN CHAT SAFELY
    # =====================================================

    def open_chat(self):

        try:

            info("OPENING E2EE CHAT")

            self.driver.get(
                f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}"
            )

            self.wait_for_page_ready(60)

            self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@contenteditable='true']"
                    )
                )
            )

            success("CHAT FULLY LOADED")

            return True

        except Exception as e:

            error(f"CHAT OPEN FAILED : {e}")

            return False

    # =====================================================
    #                   SEND MESSAGE
    # =====================================================

    def send_message(self, text):

        retries = 3

        for attempt in range(retries):

            try:

                # ============================================
                # VERIFY TAB ALIVE
                # ============================================

                self.driver.execute_script(
                    "return document.readyState"
                )

                # ============================================
                # WAIT PAGE FULLY READY
                # ============================================

                self.wait_for_page_ready(60)

                # ============================================
                # WAIT MESSAGE BOX
                # ============================================

                box = self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[@contenteditable='true']"
                        )
                    )
                )

                # ============================================
                # WAIT CLICKABLE
                # ============================================

                self.wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//div[@contenteditable='true']"
                        )
                    )
                )

                # ============================================
                # FOCUS BOX
                # ============================================

                self.driver.execute_script(
                    "arguments[0].focus();",
                    box
                )

                time.sleep(1)

                # ============================================
                # REMOVE STUCK STATE
                # ============================================

                box.send_keys(Keys.ESCAPE)

                time.sleep(0.5)

                final_msg = (
                    f"{self.haters_name} {text}"
                ).strip()

                # ============================================
                # TYPE MESSAGE SLOWLY
                # ============================================

                for char in final_msg:

                    box.send_keys(char)

                    time.sleep(0.02)

                # ============================================
                # WAIT BEFORE SEND
                # ============================================

                time.sleep(1)

                # ============================================
                # SEND MESSAGE
                # ============================================

                box.send_keys(Keys.ENTER)

                # ============================================
                # WAIT SEND COMPLETE
                # ============================================

                time.sleep(3)

                # ============================================
                # VERIFY STILL ALIVE
                # ============================================

                self.driver.execute_script(
                    "return document.readyState"
                )

                return True

            except (
                TimeoutException,
                StaleElementReferenceException,
                WebDriverException,
                Exception
            ) as e:

                error(
                    f"SEND RETRY {attempt+1}/3 : {e}"
                )

                time.sleep(5)

                try:

                    self.driver.refresh()

                    self.wait_for_page_ready(60)

                except:
                    pass

        return False

    # =====================================================
    #               RECOVER FROM TAB CRASH
    # =====================================================

    def recover_driver(self):

        try:

            error("TAB CRASH DETECTED")

            try:
                self.driver.quit()
            except:
                pass

            info("RESTARTING DRIVER")

            if not self.setup_driver():
                return False

            if not self.login_with_cookies():
                return False

            if not self.open_chat():
                return False

            success("RECOVERY SUCCESSFUL")

            return True

        except Exception as e:

            error(f"RECOVERY FAILED : {e}")

            return False

    # =====================================================
    #                       START
    # =====================================================

    def start(self):

        clear_screen()

        info("LOADING CONFIGURATION")

        if not self.auto_load():
            return

        if not self.setup_driver():
            return

        if not self.login_with_cookies():
            return

        if not self.open_chat():
            return

        success("MESSAGE SENDING STARTED")

        count = 0

        while True:

            try:

                # ============================================
                # VERIFY TAB ALIVE
                # ============================================

                self.driver.execute_script(
                    "return document.readyState"
                )

            except:

                if not self.recover_driver():
                    time.sleep(10)

                    continue

            for msg in self.messages:

                current_time = get_current_time()

                sent = self.send_message(msg)

                count += 1

                short_msg = (
                    msg[:60] + "..."
                    if len(msg) > 60
                    else msg
                )

                status = "SUCCESS" if sent else "FAILED"

                # =================================================
                #               STABLE SINGLE-LINE LOG
                # =================================================

                log(
                    f"[MSG #{count}] "
                    f"[TARGET: {self.target_uid}] "
                    f"[TIME: {current_time}] "
                    f"[STATUS: {status}] "
                    f"[MESSAGE: {short_msg}]"
                )

                # =================================================
                #                   HEARTBEAT
                # =================================================

                log(
                    f"[ALIVE] BOT RUNNING | "
                    f"MSG #{count} | "
                    f"{current_time}"
                )

                log("───────────────────────────────────────────────────────────────")

                # =================================================
                #               SAFE DELAY
                # =================================================

                time.sleep(self.delay)


# =========================================================
#                       RUN SCRIPT
# =========================================================

if __name__ == "__main__":

    bot = FacebookMessenger()

    bot.start()
