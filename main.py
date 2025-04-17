import os
import time
import telebot

# Получаем токен и ID из переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("ОШИБКА: Переменные окружения TELEGRAM_TOKEN или CHAT_ID не установлены!")
    exit()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Бот работает! Привет!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(CHAT_ID, f"Ты написал: {message.text}")

# Бесконечный polling
while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)
