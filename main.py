import os
import sys
import time
import random
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

        # RANDOMIZED MEMORY CLEANUP
        self.cleanup_interval = random.randint(8, 15)
        
        # DRIVER RESTART TRACKER
        self.restart_count = 0
        self.max_restart = 999999

    def safe_wait(self, condition, timeout=60):
        try:
            return WebDriverWait(self.driver, timeout, poll_frequency=0.5).until(condition)
        except TimeoutException:
            return False

    def driver_alive(self):
        try:
            self.driver.execute_script("return 1")
            return True
        except Exception as e:
            error(f"DRIVER DEAD : {e}")
            return False

    def recover_driver(self):
        try:
            info("STARTING DRIVER RECOVERY (HUMAN DELAY SIMULATION)")
            self.restart_count += 1
            try:
                self.driver.quit()
            except:
                pass

            time.sleep(random.uniform(8, 15))

            if not self.setup_driver():
                raise Exception("NEW DRIVER FAILED")

            if not self.login_with_cookies():
                raise Exception("RE-LOGIN FAILED")

            self.driver.get(f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}")

            loaded = self.safe_wait(lambda d: d.execute_script("return document.readyState") == "complete", 120)
            if not loaded:
                raise Exception("CHAT LOAD FAILED")

            ready = self.safe_wait(EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']")), 120)
            if not ready:
                raise Exception("CHAT BOX FAILED")

            success(f"DRIVER RECOVERY SUCCESS | RESTART #{self.restart_count}")
            return True
        except Exception as e:
            error(f"RECOVERY FAILED : {e}")
            return False

    def soft_refresh_chat(self):
        try:
            info("SOFT RESETTING CHAT TAB FOR MEMORY")
            self.driver.get("about:blank")
            time.sleep(random.uniform(2, 4))

            self.driver.get(f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}")

            loaded = self.safe_wait(lambda d: d.execute_script("return document.readyState") == "complete", 120)
            if not loaded:
                raise Exception("CHAT PAGE LOAD FAILED")

            ready = self.safe_wait(EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']")), 120)
            if not ready:
                raise Exception("CHAT BOX LOAD FAILED")

            success("TAB SOFT RESET COMPLETE")
            return True
        except Exception as e:
            error(f"SOFT RESET FAILED : {e}")
            return False

    def auto_load(self):
        try:
            self.cookie_str = open("cookies.txt", "r", encoding="utf-8").read().strip()
            self.target_uid = open("target_uid.txt", "r", encoding="utf-8").read().strip()
            self.messages = [x.strip() for x in open("messages.txt", "r", encoding="utf-8") if x.strip()]

            if os.path.exists("hatersname.txt"):
                self.haters_name = open("hatersname.txt", "r", encoding="utf-8").read().strip()

            if os.path.exists("time.txt"):
                self.delay = int(open("time.txt").read().strip())

            if not self.cookie_str or not self.target_uid or not self.messages:
                raise Exception("FILES EMPTY OR MISSING")

            success("ALL FILES AUTO-LOADED SUCCESSFULLY")
            log(f"[CONFIG] [TARGET: {self.target_uid}] [TOTAL_MSGS: {len(self.messages)}] [BASE DELAY: {self.delay}s]")
            return True
        except Exception as e:
            error(f"AUTO LOAD FAILED : {e}")
            return False

    def setup_driver(self):
        try:
            options = Options()
            options.binary_location = "/usr/bin/chromium"
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.page_load_strategy = "eager"

            # MEMORY & CRASH FIXES
            options.add_argument("--memory-pressure-off")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-gpu")
            options.add_argument("--max_old_space_size=128")

            # PRIVACY & STEALTH (ANTI-SUSPENSION)
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-notifications")
            options.add_argument("--window-size=1440,900")
            options.add_argument("--log-level=3")
            
            # REALISTIC USER AGENT TO SPOOF HEADLESS DETECTION
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

            options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument("--disable-blink-features=AutomationControlled")

            service = Service("/usr/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=options)

            self.driver.set_page_load_timeout(120)
            self.driver.set_script_timeout(120)
            self.wait = WebDriverWait(self.driver, 40)

            # ADVANCED JAVASCRIPT SPOOFING
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")

            success("STEALTH CHROME DRIVER STARTED SUCCESSFULLY")
            return True
        except Exception as e:
            error(f"DRIVER ERROR : {e}")
            return False

    def login_with_cookies(self):
        try:
            info("OPENING FACEBOOK SECURELY")
            self.driver.get("https://www.facebook.com")

            loaded = self.safe_wait(lambda d: d.execute_script("return document.readyState") == "complete", 60)
            if not loaded:
                raise Exception("FACEBOOK LOAD TIMEOUT")

            cookies = self.cookie_str.split(";")
            added = 0

            for cookie in cookies:
                if "=" in cookie:
                    name, value = cookie.strip().split("=", 1)
                    try:
                        self.driver.add_cookie({
                            "name": name,
                            "value": value,
                            "domain": ".facebook.com",
                            "path": "/"
                        })
                        added += 1
                    except:
                        pass

            success(f"COOKIES INJECTED : {added}")
            
            # RANDOM PAUSE BEFORE NAVIGATING TO MESSENGER
            time.sleep(random.uniform(2, 4))
            self.driver.get("https://www.facebook.com/messages")

            loaded = self.safe_wait(lambda d: d.execute_script("return document.readyState") == "complete", 60)
            if not loaded:
                raise Exception("MESSENGER LOAD FAILED")

            ready = self.safe_wait(EC.presence_of_element_located((By.XPATH, "//div[@role='navigation']")), 60)
            if not ready:
                raise Exception("MESSENGER UI NOT FOUND")

            success("COOKIE LOGIN VERIFIED AND SUCCESSFUL")
            return True
        except Exception as e:
            error(f"COOKIE LOGIN FAILED : {e}")
            return False

    def get_message_box(self):
        return self.safe_wait(EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']")), 120)

    def send_message(self, text):
        try:
            if not self.driver_alive():
                return False

            loaded = self.safe_wait(lambda d: d.execute_script("return document.readyState") == "complete", 120)
            if not loaded:
                raise Exception("PAGE NOT READY")

            box = self.get_message_box()
            if not box:
                raise Exception("MESSAGE BOX NOT INTERACTABLE")

            # SCROLL & FOCUS LIKE A HUMAN
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", box)
            time.sleep(random.uniform(0.5, 1.2))
            self.driver.execute_script("arguments[0].focus();", box)

            final_msg = f"{self.haters_name} {text}".strip()

            # CLEAR BOX
            self.driver.execute_script("arguments[0].innerHTML = '';", box)
            time.sleep(random.uniform(0.4, 0.8))

            # =================================================
            #     HUMAN-LIKE CHARACTER BY CHARACTER TYPING 
            # =================================================
            # Isse har emoji aur fancy font browser DOM engine me
            # natural speed par simulate hoga jisse ban secure rahega.
            for char in final_msg:
                self.driver.execute_script(
                    """
                    var element = arguments[0];
                    var character = arguments[1];
                    element.focus();
                    document.execCommand('insertText', false, character);
                    """, 
                    box, 
                    char
                )
                # Insaan ke type karne ki random speed interval (50ms to 250ms)
                time.sleep(random.uniform(0.05, 0.25))

            # THINKING DELAY BEFORE SENDING
            time.sleep(random.uniform(1.2, 3.0))

            # HIT ENTER TO SEND
            box.send_keys(Keys.ENTER)

            # REAL DOM VERIFICATION
            sent = self.safe_wait(lambda d: d.execute_script("return arguments[0].innerText.trim() === '';", box), 45)
            if not sent:
                raise Exception("MESSAGE STUCK IN BOX")

            # POST-SEND STABILITY PAUSE
            time.sleep(random.uniform(1.0, 2.5))
            return True

        except Exception as e:
            error(f"SEND FAILED : {e}")
            try:
                self.soft_refresh_chat()
            except:
                pass
            return False

    def start(self):
        clear_screen()
        info("LOADING ANTI-BAN BOT CONFIGURATION")

        if not self.auto_load():
            return
        if not self.setup_driver():
            return
        if not self.login_with_cookies():
            return

        info("OPENING SECURE E2EE CHAT TARGET")
        self.driver.get(f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}")

        loaded = self.safe_wait(lambda d: d.execute_script("return document.readyState") == "complete", 60)
        if not loaded:
            error("CHAT TARGET PAGE TIMEOUT")
            return

        chat_ready = self.safe_wait(EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']")), 60)
        if not chat_ready:
            error("TARGET CHAT BOX FAILED TO INITIALIZE")
            return

        success("SAFE MESSAGE SENDING STARTED")
        count = 0

        while True:
            for msg in self.messages:
                if not self.driver_alive():
                    error("CRASH DETECTED. INITIATING AUTO RECOVERY...")
                    if not self.recover_driver():
                        error("CRITICAL: RECOVERY FAILED")
                        return
                    continue

                current_time = get_current_time()
                sent = self.send_message(msg)
                count += 1

                # SMART INTERVALS FOR REFRESH & RESTS
                if count % 35 == 0:
                    info("FULL COMPREHENSIVE RESTART FOR DRIVER HEALTH")
                    if not self.recover_driver():
                        return
                elif count % self.cleanup_interval == 0:
                    self.soft_refresh_chat()
                    # Clean interval ko har baar random set karein taaki pattern pakda na jaye
                    self.cleanup_interval = random.randint(8, 15)

                # ADVANCED HUMAN REST LOGIC (ANTI-DETECTION)
                # Har 12-15 msgs ke baad insaan ki tarah thoda rest lega bot
                if count % random.randint(12, 16) == 0:
                    nap_time = random.randint(20, 45)
                    info(f"SIMULATING HUMAN COFFEE BREAK: TAKING REST FOR {nap_time} SECONDS...")
                    time.sleep(nap_time)

                short_msg = msg[:50] + "..." if len(msg) > 50 else msg
                status = "SUCCESS" if sent else "FAILED"

                log(f"[MSG #{count}] [TARGET: {self.target_uid}] [TIME: {current_time}] [STATUS: {status}]")
                log(f"[LIVE] BOT ACTIVE | MSG: {short_msg}")
                log("───────────────────────────────────────────────────────────────")

                # RANDOMIZED SAFE DELAY LOOP
                # Agar user ne 10s set kiya hai toh har baar static 10s nahi, variable sleep hoga
                random_variance = random.randint(-3, 6)
                actual_delay = max(4, self.delay + random_variance)

                for _ in range(actual_delay):
                    time.sleep(1)
                    if not self.driver_alive():
                        error("CRASH DETECTED IN DELAY INTERVAL. RECOVERING...")
                        if not self.recover_driver():
                            return
                        break

# =========================================================
#                       RUN SCRIPT
# =========================================================
if __name__ == "__main__":
    bot = FacebookMessenger()
    bot.start()
        
