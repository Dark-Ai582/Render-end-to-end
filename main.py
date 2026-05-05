import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================= COLORS =================
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'

    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    PRIME_RED = '\033[38;5;196m'
    PRIME_YELLOW = '\033[38;5;226m'
    PRIME_ORANGE = '\033[38;5;208m'
    PRIME_MAROOM = '\033[38;5;88m'
    PRIME_PURPLE = '\033[38;5;135m'
    PRIME_BLUE = '\033[38;5;39m'


# ================= UI FUNCTIONS =================
def clear_screen():
    pass


def print_logo():
    print(f"""{Colors.PRIME_MAROOM}{Colors.BOLD}
------------------------------------------------
        {Colors.PRIME_YELLOW}{Colors.BOLD}E2E INBOX SERVER BY COOKIE{Colors.RESET}
        {Colors.PRIME_YELLOW}{Colors.BOLD}AUTO LOAD TOOL{Colors.RESET}
        {Colors.PRIME_YELLOW}{Colors.BOLD}TOOL BY SATISH MUTHMAARE{Colors.RESET}
{Colors.PRIME_MAROOM}{Colors.BOLD}------------------------------------------------
{Colors.RESET}""")


def success(msg):
    print(f"{Colors.GREEN}{Colors.BOLD}✓ {msg}{Colors.RESET}")


def error(msg):
    print(f"{Colors.RED}{Colors.BOLD}✗ {msg}{Colors.RESET}")


def info(msg):
    print(f"{Colors.BLUE}{Colors.BOLD}ℹ {msg}{Colors.RESET}")


def separator():
    print(f"{Colors.CYAN}{'-' * 50}{Colors.RESET}")


def get_current_time():
    return time.strftime("%d-%m-%Y %I:%M:%S %p")


# ================= MAIN CLASS =================
class FacebookMessenger:

    def __init__(self):
        self.driver = None
        self.wait = None
        self.cookie_str = ""
        self.target_uid = ""
        self.messages = []
        self.haters_name = ""
        self.delay = 10

    # ---------- AUTO LOAD ----------
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
                raise Exception("Files empty or missing")

            success("All FILES AUTO-LOADED SUCCESSFULLY")
            return True

        except Exception as e:
            error(f"Auto-load failed: {e}")
            return False

    # ---------- LOGIN ----------
    def setup_driver(self):
        try:
            options = Options()
            options.add_argument("--headless")

            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            options.add_argument("--width=1920")
            options.add_argument("--height=1080")

            options.binary_location = "/usr/bin/firefox"

            service = Service("/usr/local/bin/geckodriver")

            self.driver = webdriver.Firefox(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 40)

            success("FIREFOX DRIVER STARTED")
            return True

        except Exception as e:
            error(f"Driver error: {e}")
            return False

    # ---------- LOGIN WITH COOKIES ----------
    def login_with_cookies(self):
        try:
            self.driver.get("https://www.facebook.com")
            time.sleep(5)

            cookies = self.cookie_str.split(";")
            for cookie in cookies:
                if "=" in cookie:
                    name, value = cookie.strip().split("=", 1)
                    self.driver.add_cookie({
                        "name": name,
                        "value": value,
                        "domain": ".facebook.com"
                    })

            self.driver.get("https://www.facebook.com/messages")
            time.sleep(8)

            success("Logged in using cookies")
            return True

        except Exception as e:
            error(f"Cookie login failed: {e}")
            return False

    # ---------- SEND MESSAGE ----------
    def send_message(self, text):
        try:
            box = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']"))
            )

            self.driver.execute_script("arguments[0].focus();", box)
            time.sleep(0.4)

            final_msg = f"{self.haters_name} {text}".strip()

            for ch in final_msg:
                box.send_keys(ch)
                time.sleep(0.03)

            time.sleep(0.4)
            box.send_keys(Keys.ENTER)

        except Exception as e:
            error(f"Send failed: {e}")

    # ---------- START ----------
    def start(self):
        clear_screen()
        print_logo()

        print(f"{Colors.PRIME_ORANGE}{Colors.BOLD}[ INFO ] Loading configuration...!{Colors.RESET}")
        print()

        if not self.auto_load():
            return

        if not self.setup_driver():
            return

        if not self.login_with_cookies():
            return

        self.driver.get(f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}")
        time.sleep(8)

        success("MESSAGES SENDING STARTED")
        print()
        separator()
        print()
        
        time.sleep(2)
        
        clear_screen()

        count = 0
        while True:
            for msg in self.messages:
                self.send_message(msg)
                count += 1

                current_time = get_current_time()
                message = msg

                print(f"{Colors.PRIME_BLUE}{Colors.BOLD}__________________________________________________{Colors.RESET}")
                print(f"{Colors.PRIME_BLUE}│{Colors.RESET} {Colors.YELLOW}{Colors.BOLD} E2E-Message #{count}{Colors.RESET}")
                print(f"{Colors.PRIME_BLUE}│{Colors.RESET}")
                print(f"{Colors.PRIME_BLUE}│{Colors.RESET} {Colors.PRIME_PURPLE}{Colors.BOLD} [ 🎯 ] TARGET 🆔 ={Colors.RESET} "
                      f"{Colors.WHITE}{Colors.BOLD}{self.target_uid}{Colors.RESET}")
                print(f"{Colors.PRIME_BLUE}│{Colors.RESET} {Colors.PRIME_PURPLE}{Colors.BOLD} [ 📝 ] MESSAGE ={Colors.RESET} "
                      f"{Colors.WHITE}{Colors.BOLD}{message[:40]}{'...' if len(message) > 40 else ''}{Colors.RESET}")
                print(f"{Colors.PRIME_BLUE}│{Colors.RESET} {Colors.PRIME_PURPLE}{Colors.BOLD} [ 🕒 ] TIME ={Colors.RESET} "
                      f"{Colors.WHITE}{Colors.BOLD}{current_time}{Colors.RESET}")
                print(f"{Colors.PRIME_BLUE}│{Colors.RESET} {Colors.PRIME_PURPLE}{Colors.BOLD} [ 📊 ] STATUS ={Colors.RESET} "
                      f"{Colors.GREEN}{Colors.BOLD}✓ Successfully Sent By Satish Muthmaare{Colors.RESET}")
                print(f"{Colors.PRIME_BLUE}{Colors.BOLD}__________________________________________________{Colors.RESET}")

                time.sleep(self.delay)


# ================= RUN =================
if __name__ == "__main__":
    bot = FacebookMessenger()
    bot.start()
