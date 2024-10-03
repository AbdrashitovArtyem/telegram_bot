import requests
from bs4 import BeautifulSoup

url = 'https://randstuff.ru/fact/'

def get_fact():
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Используйте правильный параметр для поиска по id
        block = soup.find('div', id='fact')
        table = block.find('table')
        
        # Если блок найден, возвращаем его текст
        if table:
            return table.get_text(strip=True)
        else:
            return 'Блок с указанным id не найден.'
    else:
        return f'Ошибка при выполнении запроса: {response.status_code}'