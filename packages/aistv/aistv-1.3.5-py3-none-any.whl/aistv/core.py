# aistv.py
import subprocess
import sys
import sqlite3
import time

# Tự cài thư viện nếu thiếu
def install_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

install_package("groq")
install_package("requests")

from groq import Groq

API_KEYS = [
    "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",
    # Thêm key phụ tại đây nếu muốn:
    # "your_second_key",
]

DB_FILE = "usage.db"
SPAM_DELAY_SECONDS = 5

FREE_MAX_REQUESTS = 20
NORMAL_MAX_REQUESTS = 30
VIP_MAX_REQUESTS = None

TOKEN_VIP_SET = {
    "aistv",
    "phuc",
}

TOKEN_NORMAL_SET = {
    "tokengsk_...",
}

MODEL_MAP = {
    "Chat-ai-stv-3.5": "meta-llama/llama-3-8b-instruct",
    "Chat-ai-stv-4.0": "meta-llama/llama-3-70b-instruct",
    "Chat-ai-stv-2.3": "meta-llama/llama-4-maverick-17b-128e-instruct",
    "Chat-ai-stv-4.5": "mistralai/mixtral-8x7b-instruct",
    "Chat-ai-stv-5.0": "google/gemma-7b-it",
}

class aistv:
    def __init__(self, token, model, system_prompt=None):
        if token is None:
            raise ValueError("Bạn phải truyền token khi khởi tạo aistv")
        if model is None:
            raise ValueError("Bạn phải truyền model khi khởi tạo aistv")

        # Bắt buộc model phải nằm trong MODEL_MAP, dùng key nguyên gốc
        if model not in MODEL_MAP:
            raise ValueError(f"Mô hình không hợp lệ: {model}. Dùng: {list(MODEL_MAP.keys())}")

        self.model_key = model
        self.model = MODEL_MAP[self.model_key]
        self.system_prompt = system_prompt or "Tôi là AI STV, được phát triển bởi Trọng Phúc."
        self.token = token

        self.api_key_index = 0
        self.client = Groq(api_key=API_KEYS[self.api_key_index])

        self.history = [{"role": "system", "content": self.system_prompt}]

        if token in TOKEN_VIP_SET:
            self.max_requests = VIP_MAX_REQUESTS
            self.user_id = token
        elif token in TOKEN_NORMAL_SET:
            self.max_requests = NORMAL_MAX_REQUESTS
            self.user_id = token
        else:
            self.max_requests = FREE_MAX_REQUESTS
            self.user_id = "free_user"

        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage (
                user_id TEXT PRIMARY KEY,
                count INTEGER,
                last_time REAL,
                last_date TEXT
            )
        ''')
        self.conn.commit()
        self._init_user()

    def _init_user(self):
        today = time.strftime("%Y-%m-%d")
        self.cursor.execute("SELECT * FROM usage WHERE user_id = ?", (self.user_id,))
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO usage (user_id, count, last_time, last_date) VALUES (?, ?, ?, ?)",
                (self.user_id, 0, 0, today)
            )
            self.conn.commit()

    def _get_usage(self):
        self.cursor.execute("SELECT count, last_time, last_date FROM usage WHERE user_id = ?", (self.user_id,))
        row = self.cursor.fetchone()
        return {"count": row[0], "last_time": row[1], "last_date": row[2]} if row else {"count": 0, "last_time": 0, "last_date": time.strftime("%Y-%m-%d")}

    def _save_usage(self, count, last_time, last_date):
        self.cursor.execute(
            "UPDATE usage SET count = ?, last_time = ?, last_date = ? WHERE user_id = ?",
            (count, last_time, last_date, self.user_id)
        )
        self.conn.commit()

    def _switch_api_key(self):
        if self.api_key_index + 1 < len(API_KEYS):
            self.api_key_index += 1
            self.client = Groq(api_key=API_KEYS[self.api_key_index])
            return True
        return False

    def chat(self, prompt: str) -> str:
        usage = self._get_usage()
        now = time.time()
        today = time.strftime("%Y-%m-%d")

        if usage["last_date"] != today:
            usage["count"] = 0
            usage["last_date"] = today

        if self.max_requests is not None and usage["count"] >= self.max_requests:
            return f"⚠️ Đã hết {self.max_requests} lượt/ngày. Thử lại mai hoặc xin thêm quyền. https://discord.gg/Ze7RTExgdv"

        if now - usage["last_time"] < SPAM_DELAY_SECONDS:
            wait_time = SPAM_DELAY_SECONDS - int(now - usage["last_time"])
            return f"⚠️ Vui lòng chờ thêm {wait_time} giây giữa các câu hỏi."

        self.history.append({"role": "user", "content": prompt})

        while True:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=self.history,
                    model=self.model,
                    stream=False,
                )
                reply = chat_completion.choices[0].message.content
                self.history.append({"role": "assistant", "content": reply})

                if self.max_requests is not None:
                    usage["count"] += 1
                    usage["last_time"] = now
                    self._save_usage(usage["count"], usage["last_time"], usage["last_date"])

                return reply.strip()

            except Exception as e:
                if "quota" in str(e).lower() or "token" in str(e).lower():
                    if not self._switch_api_key():
                        return f"⚠️ API hết hạn hoặc lỗi: {e}"
                else:
                    return f"⚠️ Lỗi khi gọi API: {e}"