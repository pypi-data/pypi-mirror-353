import requests
import os
import json
import time

SYSTEM_PROMPT = """
Tôi là AI STV, được phát triển bởi Trọng Phúc.
"""

USAGE_LOG = "ip_usage.json"
TOKENS_FILE = "files.txt"
MAX_REQUESTS_PER_DAY = 20
SPAM_DELAY_SECONDS = 5

def get_user_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except:
        return "unknown"

def load_usage():
    if os.path.exists(USAGE_LOG):
        with open(USAGE_LOG, "r") as f:
            return json.load(f)
    return {}

def save_usage(data):
    with open(USAGE_LOG, "w") as f:
        json.dump(data, f)

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

class STVBot:
    def __init__(self, user_token=None, system_prompt=SYSTEM_PROMPT):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.system_prompt = system_prompt
        self.model = "deepseek/deepseek-r1-0528-qwen3-8b:free"
        self.history = [{"role": "system", "content": system_prompt}]
        self.user_ip = get_user_ip()
        self.token = user_token.strip() if user_token else None
        self.free_mode = self.token is None
        self.usage_data = load_usage()
        self.tokens = load_tokens()
        self.last_request_time = 0

        # Khởi tạo dữ liệu cho IP nếu chưa có
        if self.user_ip not in self.usage_data:
            self.usage_data[self.user_ip] = {
                "count": 0,
                "last_time": 0
            }

    def get_valid_test_token(self):
        for token in self.tokens:
            if self.validate_token(token):
                return token
        return self.tokens[0] if self.tokens else None

    def validate_token(self, token):
        try:
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
                    "max_tokens": 10
                },
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def chat(self, prompt):
        now = time.time()
        usage = self.usage_data[self.user_ip]

        # Giới hạn số lần hỏi mỗi ngày
        if usage["count"] >= MAX_REQUESTS_PER_DAY:
            return (
                "⚠️ Bạn đã sử dụng hết giới hạn 20 câu hỏi miễn phí trong ngày.\n"
                "Vui lòng nhập token riêng của bạn để tiếp tục sử dụng AI STV.\n"
                "Nếu chưa có, hãy vào Discord để được hỗ trợ miễn phí:\n"
                "👉 https://discord.gg/Ze7RTExgdv"
            )

        # Chống spam: yêu cầu cách nhau ít nhất 5 giây
        if now - usage.get("last_time", 0) < SPAM_DELAY_SECONDS:
            return f"⚠️ Vui lòng chờ {SPAM_DELAY_SECONDS} giây giữa mỗi câu hỏi."

        # Gán token nếu đang dùng free mode
        if self.free_mode:
            self.token = self.get_valid_test_token()
            if not self.token:
                return "❌ Không có token test khả dụng. Vui lòng thử lại sau."

        self.history.append({"role": "user", "content": prompt})
        body = {
            "model": self.model,
            "messages": self.history,
            "max_tokens": 300,
            "temperature": 0.7,
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "STV Chat"
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=body, timeout=15)
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})

            # Cập nhật log
            usage["count"] += 1
            usage["last_time"] = now
            self.usage_data[self.user_ip] = usage
            save_usage(self.usage_data)

            return reply.strip()
        except Exception as e:
            return f"⚠️ Lỗi khi kết nối API: {e}"