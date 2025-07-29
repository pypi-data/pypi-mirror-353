from aistv.aistv import aistv

bot = aistv()  # Khởi tạo class aistv
token = input("🔑 Nhập token để thêm vào thư viện: ").strip()
result = bot.add_token(token)
print(result)