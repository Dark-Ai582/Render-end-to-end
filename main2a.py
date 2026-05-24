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
        self.delay = 10

    # =====================================================
    #               SAFE WAIT FUNCTION
    # =====================================================

    def safe_wait(self, condition, timeout=60):

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
                    open("time.txt").read().strip()
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

            service = Service("/usr/bin/chromedriver")

            self.driver = webdriver.Chrome(
                service=service,
                options=options
            )

            self.wait = WebDriverWait(
                self.driver,
                40
            )

            success("CHROME DRIVER STARTED")
            success("LOW MEMORY MODE ENABLED")
            success("RAILWAY LOGGING FIX ENABLED")

            return True

        except Exception as e:

            error(f"DRIVER ERROR : {e}")

            return False

    # =====================================================
    #           LOGIN USING COOKIES (STABLE)
    # =====================================================

    def login_with_cookies(self):

        try:

            info("OPENING FACEBOOK")

            self.driver.get(
                "https://www.facebook.com"
            )

            # WAIT PAGE LOAD
            self.safe_wait(
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete",
                60
            )

            cookies = self.cookie_str.split(";")

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

            success(f"COOKIES LOADED : {added}")

            # OPEN MESSENGER
            self.driver.get(
                "https://www.facebook.com/messages"
            )

            # WAIT COMPLETE LOAD
            self.safe_wait(
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete",
                60
            )

            # WAIT CHAT UI
            loaded = self.safe_wait(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@role='navigation']"
                    )
                ),
                60
            )

            if not loaded:
                raise Exception("MESSENGER UI LOAD FAILED")

            success("LOGIN SUCCESSFUL")

            return True

        except Exception as e:

            error(f"COOKIE LOGIN FAILED : {e}")

            return False

    # =====================================================
    #           SEND MESSAGE (FULL STEP CONFIRM)
    # =====================================================

    def send_message(self, text):

        try:

            # =============================================
            # STEP 1 → PAGE FULLY READY
            # =============================================

            loaded = self.safe_wait(
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete",
                120
            )

            if not loaded:
                raise Exception("PAGE LOAD TIMEOUT")

            # =============================================
            # STEP 2 → MESSAGE BOX READY
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
                raise Exception("MESSAGE BOX NOT READY")

            # =============================================
            # STEP 3 → SCROLL INTO VIEW
            # =============================================

            self.driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center'
                });
                """,
                box
            )

            # =============================================
            # STEP 4 → FOCUS MESSAGE BOX
            # =============================================

            self.driver.execute_script(
                "arguments[0].focus();",
                box
            )

            focused = self.safe_wait(
                lambda d: d.execute_script(
                    "return document.activeElement === arguments[0]",
                    box
                ),
                30
            )

            if not focused:
                raise Exception("BOX FOCUS FAILED")

            # =============================================
            # STEP 5 → FINAL MESSAGE
            # =============================================

            final_msg = (
                f"{self.haters_name} {text}"
            ).strip()

            # =============================================
            # STEP 6 → CLEAR OLD TEXT
            # =============================================

            box.send_keys(
                Keys.CONTROL,
                "a"
            )

            box.send_keys(Keys.BACKSPACE)

            cleared = self.safe_wait(
                lambda d: box.text.strip() == "",
                20
            )

            if not cleared:
                raise Exception("OLD TEXT NOT CLEARED")

            # =============================================
            # STEP 7 → TYPE MESSAGE
            # =============================================

            box.send_keys(final_msg)

            typed = self.safe_wait(
                lambda d: final_msg in box.text,
                60
            )

            if not typed:
                raise Exception("MESSAGE TYPING FAILED")

            # =============================================
            # STEP 8 → SMALL STABILITY WAIT
            # =============================================

            time.sleep(1)

            # =============================================
            # STEP 9 → SEND MESSAGE
            # =============================================

            box.send_keys(Keys.ENTER)

            # =============================================
            # STEP 10 → WAIT REAL SEND COMPLETE
            # =============================================

            send_complete = self.safe_wait(
                lambda d: box.text.strip() == "",
                60
            )

            if not send_complete:
                raise Exception("MESSAGE SEND NOT CONFIRMED")

            # =============================================
            # STEP 11 → EXTRA CONFIRMATION
            # =============================================

            stable = self.safe_wait(
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete",
                30
            )

            if not stable:
                raise Exception("POST SEND STABILITY FAILED")

            # =============================================
            # STEP 12 → SAFETY WAIT
            # =============================================

            time.sleep(2)

            return True

        except Exception as e:

            error(f"SEND FAILED : {e}")

            try:

                self.driver.refresh()

                self.safe_wait(
                    lambda d: d.execute_script(
                        "return document.readyState"
                    ) == "complete",
                    120
                )

            except:
                pass

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

        info("OPENING E2EE CHAT")

        self.driver.get(
            f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}"
        )

        # WAIT PAGE LOAD
        self.safe_wait(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete",
            60
        )

        # WAIT MESSAGE BOX READY
        chat_ready = self.safe_wait(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@contenteditable='true']"
                )
            ),
            60
        )

        if not chat_ready:

            error("CHAT FAILED TO OPEN")

            return

        success("MESSAGE SENDING STARTED")

        count = 0

        while True:

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

                for _ in range(self.delay):
                      time.sleep(1)

                      # DRIVER STILL ALIVE CHECK
                      try:
                           self.driver.title
                      except:
                            error("DRIVER CRASH DETECTED")
                            return


# =========================================================
#                       RUN SCRIPT
# =========================================================

if __name__ == "__main__":

    bot = FacebookMessenger()

    bot.start()