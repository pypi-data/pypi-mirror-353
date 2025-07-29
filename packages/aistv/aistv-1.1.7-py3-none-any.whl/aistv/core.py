import requests
import os
import json
import time
from datetime import datetime

SYSTEM_PROMPT = "Tôi là AI STV"
USAGE_LOG = "ip_usage.json"
TOKENS_FILE = "files.txt"
MAX_REQUESTS_PER_DAY = 20
SPAM_DELAY_SECONDS = 5

def get_user_ip():
    try:
        return requests.get("https://api.ipify.org?format=json", timeout=5).json()["ip"]
    except:
        return "unknown"

def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        return []
    with open(TOKENS_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_tokens(tokens):
    with open(TOKENS_FILE, "w") as f:
        for t in tokens:
            f.write(t + "\n")

def validate_token(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": "nousresearch/deephermes-3-mistral-24b-preview:free",
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 5,
            },
            timeout=10,
        )
        return response.status_code == 200
    except:
        return False

def load_usage():
    if os.path.exists(USAGE_LOG):
        with open(USAGE_LOG, "r") as f:
            return json.load(f)
    return {}

def save_usage(data):
    with open(USAGE_LOG, "w") as f:
        json.dump(data, f)

class STVBot:
    def __init__(self, user_token=None, system_prompt=SYSTEM_PROMPT):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.system_prompt = system_prompt
        self.model = "nousresearch/deephermes-3-mistral-24b-preview:free"
        self.history = [{"role": "system", "content": system_prompt}]
        self.user_ip = get_user_ip()
        self.token = user_token.strip() if user_token else None
        self.free_mode = self.token is None
        self.usage_data = load_usage()
        self.tokens = load_tokens()
        self.last_call_times = {}

        if self.user_ip not in self.usage_data:
            self.usage_data[self.user_ip] = {"count": 0, "last_reset": str(datetime.today().date())}

        self._check_reset()

        if self.free_mode:
            self.token = self._get_valid_token()

    def _check_reset(self):
        today = str(datetime.today().date())
        if self.usage_data[self.user_ip]["last_reset"] != today:
            self.usage_data[self.user_ip] = {"count": 0, "last_reset": today}
            save_usage(self.usage_data)

    def _get_valid_token(self):
        for token in self.tokens:
            if validate_token(token):
                return token
        return None

    def chat(self, prompt):
        now = time.time()
        last_call = self.last_call_times.get(self.user_ip, 0)

        if now - last_call < SPAM_DELAY_SECONDS:
            return "⏳ Vui lòng chờ vài giây trước khi gửi yêu cầu tiếp theo."

        usage = self.usage_data.get(self.user_ip, {"count": 0})
        if usage["count"] >= MAX_REQUESTS_PER_DAY:
            return (
                "⚠️ Bạn đã vượt quá giới hạn 20 lượt/ngày.\n"
                "Hãy quay lại vào ngày mai hoặc dùng token riêng để tiếp tục."
            )

        if not self.token:
            return "❌ Không còn token khả dụng. Vui lòng thử lại sau."

        self.last_call_times[self.user_ip] = now
        self.history.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "STV Chat"
        }
        body = {
            "model": self.model,
            "messages": self.history,
            "max_tokens": 300,
            "temperature": 0.7,
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=body, timeout=15)
            if response.status_code != 200:
                self.tokens.remove(self.token)
                save_tokens(self.tokens)
                return "❌ Token hiện tại không hợp lệ và đã bị xoá. Vui lòng thử lại."

            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})

            self.usage_data[self.user_ip]["count"] += 1
            save_usage(self.usage_data)

            return reply.strip()
        except Exception as e:
            return f"⚠️ Lỗi khi kết nối API: {e}"

    def add_token(self, new_token):
        if new_token in self.tokens:
            return "✅ Token đã tồn tại trong hệ thống."

        if validate_token(new_token):
            self.tokens.append(new_token)
            save_tokens(self.tokens)
            return "✅ Token hợp lệ và đã được thêm thành công."
        else:
            return "❌ Token không hợp lệ."

    def ask(self, message):  # ✅ Thêm dòng này
        return self.chat(message)