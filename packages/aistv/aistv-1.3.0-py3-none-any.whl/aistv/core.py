import os
import json
import time
import requests
from groq import Groq

USAGE_LOG = "ip_usage.json"
MAX_REQUESTS_PER_DAY = 20
SPAM_DELAY_SECONDS = 5

API_KEY = "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"

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
        json.dump(data, f, indent=2)

class STVBot:
    def __init__(self, system_prompt: str = None):
        if system_prompt is None:
            system_prompt = "Tôi là AI STV, được phát triển bởi Trọng Phúc."
        self.client = Groq(api_key=API_KEY)
        self.system_prompt = system_prompt
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.history = [{"role": "system", "content": system_prompt}]
        self.user_ip = get_user_ip()
        self.usage_data = load_usage()

        if self.user_ip not in self.usage_data:
            self.usage_data[self.user_ip] = {
                "count": 0,
                "last_time": 0
            }

    def chat(self, prompt: str) -> str:
        now = time.time()
        usage = self.usage_data[self.user_ip]

        if usage["count"] >= MAX_REQUESTS_PER_DAY:
            return (
                "⚠️ Bạn đã sử dụng hết giới hạn 20 câu hỏi miễn phí trong ngày.\n"
                "Vui lòng thử lại vào ngày mai hoặc liên hệ để được cấp thêm quyền."
            )

        if now - usage.get("last_time", 0) < SPAM_DELAY_SECONDS:
            wait_time = SPAM_DELAY_SECONDS - int(now - usage.get("last_time", 0))
            return f"⚠️ Vui lòng chờ thêm {wait_time} giây giữa mỗi câu hỏi."

        self.history.append({"role": "user", "content": prompt})

        try:
            chat_completion = self.client.chat.completions.create(
                messages=self.history,
                model=self.model,
                stream=False,
            )
            reply = chat_completion.choices[0].message.content
            self.history.append({"role": "assistant", "content": reply})

            usage["count"] += 1
            usage["last_time"] = now
            self.usage_data[self.user_ip] = usage
            save_usage(self.usage_data)

            return reply.strip()

        except Exception as e:
            return f"⚠️ Lỗi khi kết nối API Groq: {e}"