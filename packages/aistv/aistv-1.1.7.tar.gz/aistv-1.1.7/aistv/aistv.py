from .core import STVBot

class aistv:
    def __init__(self, token=None):
        self.bot = STVBot(token)

    def chat(self, message):
        return self.bot.chat(message)

    def add_token(self, token):  # <- Đây là phần cần có
        return self.bot.add_token(token)