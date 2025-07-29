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
MAX_REQUESTS_PER_DAY = 20
SPAM_DELAY_SECONDS = 5

API_KEY = "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"

class STVBot:
    def __init__(self, user_id: str, system_prompt: str = None):
        if system_prompt is None:
            system_prompt = "Tôi là AI STV, được phát triển bởi Trọng Phúc."
        self.client = Groq(api_key=API_KEY)
        self.system_prompt = system_prompt
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.history = [{"role": "system", "content": system_prompt}]
        self.user_id = user_id

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

        if usage["count"] >= MAX_REQUESTS_PER_DAY:
            return (
                "⚠️ Bạn đã sử dụng hết giới hạn 20 câu hỏi miễn phí trong ngày.\n"
                "Vui lòng thử lại vào ngày mai hoặc liên hệ để được cấp thêm quyền."
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

            usage["count"] += 1
            usage["last_time"] = now
            self._save_usage(usage["count"], usage["last_time"], usage["last_date"])

            return reply.strip()

        except Exception as e:
            return f"⚠️ Lỗi khi kết nối API Groq: {e}"