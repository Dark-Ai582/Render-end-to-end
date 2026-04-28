import os
import time
import threading
from flask import Flask

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#  NEW IMPORTS (IMPORTANT)
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ================= FLASK SERVER =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running "

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ================= MAIN BOT =================
class FacebookMessenger:
    def __init__(self):
        self.driver = None
        self.wait = None

        print("Loading files...", flush=True)

        self.cookie_str = open("cookies.txt").read().strip()
        self.target_uid = open("target_uid.txt").read().strip()
        self.messages = [x.strip() for x in open("messages.txt") if x.strip()]
        self.delay = int(open("time.txt").read().strip())

        self.haters_name = ""
        if os.path.exists("hatersname.txt"):
            self.haters_name = open("hatersname.txt").read().strip()

        print("Files loaded!", flush=True)

    # ================= DRIVER SETUP =================
    def setup_driver(self):
        chrome_options = Options()

        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        print("Starting Chrome...", flush=True)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.wait = WebDriverWait(self.driver, 30)

        print("Chrome Started Successfully", flush=True)

    # ================= LOGIN =================
    def login_with_cookies(self):
        print("Opening Facebook...", flush=True)

        self.driver.get("https://www.facebook.com")
        time.sleep(3)

        print("Adding cookies...", flush=True)

        for pair in self.cookie_str.split(";"):
            if "=" in pair:
                name, value = pair.strip().split("=", 1)
                self.driver.add_cookie({
                    "name": name,
                    "value": value,
                    "domain": ".facebook.com",
                    "path": "/"
                })

        self.driver.refresh()
        time.sleep(5)

        print("Cookies loaded!", flush=True)

    # ================= SEND MESSAGE =================
    def send_message(self, text):
        try:
            box = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']"))
            )

            box.click()
            time.sleep(0.5)

            final_msg = f"{self.haters_name} {text}".strip()

            for ch in final_msg:
                box.send_keys(ch)
                time.sleep(0.02)

            box.send_keys(Keys.ENTER)

        except Exception as e:
            print("Send Error:", e, flush=True)

    # ================= MAIN START =================
    def start(self):
        print("Bot Starting...", flush=True)

        self.setup_driver()
        self.login_with_cookies()

        print("Opening chat...", flush=True)
        self.driver.get(f"https://www.facebook.com/messages/t/{self.target_uid}")
        time.sleep(10)

        print("Chat opened", flush=True)

        while True:
            for msg in self.messages:
                self.send_message(msg)
                print("Sent:", msg, flush=True)
                time.sleep(self.delay)


# ================= RUN =================
if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()

    bot = FacebookMessenger()
    bot.start()