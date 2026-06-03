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
        self.cleanup_interval = 8  # Increased slightly for realistic human pacing
        self.restart_count = 0
        
        # Local session persistence directory on Railway ephemeral disk
        self.user_data_dir = "/tmp/fb_selenium_profile"

    def safe_wait(self, condition, timeout=45):
        try:
            return WebDriverWait(self.driver, timeout, poll_frequency=1).until(condition)
        except TimeoutException:
            return False

    def driver_alive(self):
        try:
            self.driver.execute_script("return 1")
            return True
        except Exception:
            return False

    def recover_driver(self):
        """Restarts browser while strictly preserving the active session profile data."""
        try:
            info("INITIATING SEAMLESS DRIVER RECOVERY")
            self.restart_count += 1

            try:
                self.driver.quit()
            except:
                pass

            time.sleep(random.uniform(5.0, 10.0))

            if not self.setup_driver():
                raise Exception("DRIVER INITIALIZATION FAILED")

            # Directly navigate to chat. Session is preserved inside user_data_dir,
            # avoiding redundant and suspicious login/cookie injections.
            self.driver.get(f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}")

            loaded = self.safe_wait(lambda d: d.execute_script("return document.readyState") == "complete", 90)
            if not loaded:
                raise Exception("CHAT RELOAD TIMEOUT")

            success(f"DRIVER SILENTLY RECOVERED | SESSION PRESERVED | RESTART #{self.restart_count}")
            return True
        except Exception as e:
            error(f"RECOVERY ATTEMPT FAILED: {e}")
            return False

    def soft_refresh_chat(self):
        try:
            info("HUMAN-LIKE TAB REFRESH (CLEANUP)")
            self.driver.get("about:blank")
            time.sleep(random.uniform(2.0, 4.0))
            
            self.driver.get(f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}")
            
            loaded = self.safe_wait(lambda d: d.execute_script("return document.readyState") == "complete", 90)
            if not loaded:
                return False
                
            success("TAB REFRESH SUCCESSFUL")
            return True
        except Exception as e:
            error(f"SOFT REFRESH ERROR: {e}")
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
                raise Exception("REQUIRED DATA FILES ARE EMPTY")

            success("ALL CONFIGURATIONS AUTO-LOADED")
            return True
        except Exception as e:
            error(f"AUTO-LOAD CRITICAL FAILURE: {e}")
            return False

    def setup_driver(self):
        try:
            options = Options()
            options.binary_location = "/usr/bin/chromium"
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.page_load_strategy = "eager"
            
            # --- PERSISTENT SESSION DIRECTORY ---
            options.add_argument(f"--user-data-dir={self.user_data_dir}")

            # --- ADVANCED HUMAN STEALTH FINGERPRINTING ---
            options.add_argument("--window-size=1440,900")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # --- Resource & Anti-Crash Configurations ---
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-notifications")
            options.add_argument("--blink-settings=imagesEnabled=false")

            service = Service("/usr/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=options)
            
            self.driver.set_page_load_timeout(90)
            self.driver.set_script_timeout(90)
            self.wait = WebDriverWait(self.driver, 30)

            # Masking webdriver footprints
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
            """)

            return True
        except Exception as e:
            error(f"CHROME DRIVER INITIALIZATION FAILED: {e}")
            return False

    def login_with_cookies(self):
        try:
            info("CHECKING ACTIVE SESSION STATUS")
            self.driver.get("https://www.facebook.com")
            
            # Check if persistent session is already logged in
            time.sleep(3)
            if "messages" in self.driver.current_url or self.safe_wait(EC.presence_of_element_located((By.XPATH, "//div[@role='navigation']")), 10):
                success("ACTIVE PERSISTENT SESSION DETECTED. SKIPPING COOKIE INJECTION.")
                return True

            info("FRESH COOKIE INJECTION REQUIRED")
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

            success(f"INJECTED {added} SECURITY TOKENS SUCCESSFULLY")
            
            # Navigate to establish profile data saving
            self.driver.get("https://www.facebook.com/messages")
            ready = self.safe_wait(EC.presence_of_element_located((By.XPATH, "//div[@role='navigation']")), 45)
            
            if not ready:
                raise Exception("SECURE PROFILE INTERFACE UNRESPONSIVE")

            success("AUTHENTICATION INITIALIZATION COMPLETELY SECURED")
            return True
        except Exception as e:
            error(f"COOKIE BASE AUTHENTICATION FAILED: {e}")
            return False

    def simulate_human_typing(self, element, text):
        """Simulates natural human keystrokes with variable rhythmic micro-delays."""
        element.click()
        time.sleep(random.uniform(0.4, 0.8))
        
        # Clipboard integration or direct execution layer can corrupt complex stylish fonts/emojis.
        # This approach ensures character integrity while preserving humanized speed variance.
        for character in text:
            element.send_keys(character)
            # Fluid rhythmic variation to mimic authentic typing patterns
            time.sleep(random.uniform(0.04, 0.22)) 
            
        time.sleep(random.uniform(0.5, 1.2))

    def send_message(self, text):
        try:
            if not self.driver_alive():
                return False

            box = self.safe_wait(EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']")), 45)
            if not box:
                raise Exception("EDITABLE TEXT AREA UNREACHABLE")

            # Natural interaction scroll
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", box)
            self.driver.execute_script("arguments[0].focus();", box)
            time.sleep(random.uniform(0.5, 1.5))

            final_msg = f"{self.haters_name} {text}".strip() if self.haters_name else text.strip()

            # Clean workspace
            self.driver.execute_script("arguments[0].innerHTML = '';", box)
            time.sleep(0.5)

            # Humanized execution
            self.simulate_human_typing(box, final_msg)

            # Send action mimicry
            box.send_keys(Keys.ENTER)

            # Verification routine
            sent = self.safe_wait(lambda d: d.execute_script("return arguments[0].innerText.trim() === '';"), 30)
            if not sent:
                raise Exception("MESSAGE STUCK IN TRANSMISSION AREA")

            return True

        except Exception as e:
            error(f"TRANSMISSION INTERRUPTED: {e}")
            try:
                self.soft_refresh_chat()
            except:
                pass
            return False

    def start(self):
        info("PREPARING SECURE DISK INTERFACES")
        if not self.auto_load():
            return
        if not self.setup_driver():
            return
        if not self.login_with_cookies():
            return

        info("CONNECTING VIA END-TO-END ENCRYPTED GATEWAY")
        self.driver.get(f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}")

        if not self.safe_wait(EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']")), 60):
            error("TARGET GATEWAY COMMS UNRESPONSIVE. RETRYING OPERATION...")
            self.soft_refresh_chat()

        success("HUMANIZED EMULATOR ACTIVE AND SENDING")
        count = 0

        while True:
            for msg in self.messages:
                if not self.driver_alive():
                    error("CRITICAL RUNTIME DETECTED. RECOVERING LIVE SESSION...")
                    if not self.recover_driver():
                        return
                    continue

                current_time = get_current_time()
                sent = self.send_message(msg)
                count += 1

                # Clean memory bloat periodically using an dynamic scale factor
                if count % self.cleanup_interval == 0:
                    self.soft_refresh_chat()

                # Periodic silent driver rotation without session loss (every 40 messages)
                if count % 40 == 0:
                    info("PERFORMING ANTI-LEAK DRIVER ROTATION")
                    if not self.recover_driver():
                        return

                short_msg = msg[:40] + "..." if len(msg) > 40 else msg
                status = "DELIVERED" if sent else "FAILED"

                log(f"[MSG #{count}] [STATUS: {status}] [TIME: {current_time}] [CONTENT: {short_msg}]")
                log("─" * 65)

                # --- HUMAN DISTRIBUTED DELAY INTERVAL ---
                # Fixed delay ko mitigate karke dynamic range calculate karna compulsory hai
                actual_delay = self.delay + random.randint(-3, 5)
                if actual_delay < 2: 
                    actual_delay = 2

                for _ in range(actual_delay):
                    time.sleep(1)
                    if not self.driver_alive():
                        break

if __name__ == "__main__":
    bot = FacebookMessenger()
    bot.start()
