import subprocess
import sys
import sqlite3
import time

# Tự cài groq và requests nếu chưa có
def install_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

install_package("groq")
install_package("requests")

import requests
from groq import Groq

DB_FILE = "usage.db"
SPAM_DELAY_SECONDS = 5

# Giới hạn theo loại token
FREE_MAX_REQUESTS = 20
NORMAL_MAX_REQUESTS = 30
VIP_MAX_REQUESTS = None  # Không giới hạn

# Ví dụ token thường và token VIP bạn quản lý
TOKEN_VIP_SET = {
    "aistv",
    "phuc",
}

TOKEN_NORMAL_SET = {
    "aistvgsk_wr9rnhdGCQYCaeAEFQusWGdyb3FYF4LVKrxM0I9JDSGkZIVIymwPgsk_wr9rnhdGCQYCaeAEFQusWGdyb3FYF4LVKrxM0I9JDSGkZIVIymwPgsk_wr9rnhdGCQYCaeAEFQusWGdyb3FYF4LVKrxM0I9JDSGkZIVIymwPgsk_wr9rnhdGCQYCaeAEFQusWGdyb3FYF4LVKrxM0I9JDSGkZIVIymwP",
    "tokengsk_wr9rnhdGCQYCaeAEFQusWGdyb3FYF4LVKrxM0I9JDSGkZIVIymwP",
}

API_KEY = "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"

class STVBot:
    def __init__(self, token: str = None, system_prompt: str = None):
        """
        token: None (free user), or token string (normal or VIP)
        """
        if not system_prompt:
            system_prompt = "Tôi là AI STV, được phát triển bởi Trọng Phúc."
        self.client = Groq(api_key=API_KEY)
        self.system_prompt = system_prompt
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.history = [{"role": "system", "content": self.system_prompt}]

        self.token = token
        if token is None:
            self.max_requests = FREE_MAX_REQUESTS
            self.user_id = "free_user"
        elif token in TOKEN_VIP_SET:
            self.max_requests = VIP_MAX_REQUESTS
            self.user_id = token
        elif token in TOKEN_NORMAL_SET:
            self.max_requests = NORMAL_MAX_REQUESTS
            self.user_id = token
        else:
            # Token không hợp lệ tính free
            self.max_requests = FREE_MAX_REQUESTS
            self.user_id = "free_user"

        # Kết nối DB SQLite
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

        # Khởi tạo dữ liệu user nếu chưa có
        self._init_user()

    def _init_user(self):
        today = time.strftime("%Y-%m-%d")
        self.cursor.execute("SELECT * FROM usage WHERE user_id = ?", (self.user_id,))
        row = self.cursor.fetchone()
        if not row:
            self.cursor.execute(
                "INSERT INTO usage (user_id, count, last_time, last_date) VALUES (?, ?, ?, ?)",
                (self.user_id, 0, 0, today)
            )
            self.conn.commit()

    def _get_usage(self):
        self.cursor.execute("SELECT count, last_time, last_date FROM usage WHERE user_id = ?", (self.user_id,))
        row = self.cursor.fetchone()
        if row:
            return {"count": row[0], "last_time": row[1], "last_date": row[2]}
        else:
            return {"count": 0, "last_time": 0, "last_date": time.strftime("%Y-%m-%d")}

    def _save_usage(self, count, last_time, last_date):
        self.cursor.execute(
            "UPDATE usage SET count = ?, last_time = ?, last_date = ? WHERE user_id = ?",
            (count, last_time, last_date, self.user_id)
        )
        self.conn.commit()

    def chat(self, prompt: str) -> str:
        usage = self._get_usage()
        now = time.time()
        today = time.strftime("%Y-%m-%d")

        # Reset count nếu khác ngày
        if usage["last_date"] != today:
            usage["count"] = 0
            usage["last_date"] = today

        if self.max_requests is not None and usage["count"] >= self.max_requests:
            return (
                f"⚠️ Bạn đã sử dụng hết giới hạn {self.max_requests} câu hỏi trong ngày.\n"
                "Vui lòng thử lại vào ngày mai hoặc liên hệ để được cấp thêm quyền.https://discord.gg/Ze7RTExgdv"
            )

        if now - usage["last_time"] < SPAM_DELAY_SECONDS:
            wait_time = SPAM_DELAY_SECONDS - int(now - usage["last_time"])
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

            if self.max_requests is not None:
                usage["count"] += 1
                usage["last_time"] = now
                self._save_usage(usage["count"], usage["last_time"], usage["last_date"])

            return reply.strip()

        except Exception as e:
            return f"⚠️ Lỗi khi gọi API: {e}"