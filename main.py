import requests
import os
import re
import time
from telegram import Bot

SEARCH_KEYWORDS = ['API_KEY=', 'SECRET=', 'EMAIL=']
OUTPUT_FILE = 'github_env_leaks.txt'
GITHUB_SEARCH_URL = 'https://api.github.com/search/code'
HEADERS = {'Accept': 'application/vnd.github.v3.text-match+json'}
RESULTS_PER_PAGE = 10

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def search_github(keyword, page=1):
    params = {
        'q': f'{keyword} in:file filename:.env',
        'page': page,
        'per_page': RESULTS_PER_PAGE
    }
    response = requests.get(GITHUB_SEARCH_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
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
            for page in range(1, 2):  # лимит без авторизации
                results = search_github(keyword, page)
                for item in results:
                    info = extract_info(item)
                    if info:
                        f.write(info + '\n' + '-'*80 + '\n')
                time.sleep(2)

def send_to_telegram():
    if TELEGRAM_TOKEN and CHAT_ID and os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0:
        bot = Bot(token=TELEGRAM_TOKEN)
        with open(OUTPUT_FILE, 'rb') as f:
            bot.send_document(chat_id=CHAT_ID, document=f, filename=OUTPUT_FILE)
    else:
        print('Файл пустой или переменные окружения не установлены.')

if __name__ == '__main__':
    write_results()
    send_to_telegram()
