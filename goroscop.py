import requests
from bs4 import BeautifulSoup

associations = {
    'Овен' : 'aries',
    'Телец' : 'taurus',
    'Близнецы' : 'gemini',
    'Рак' : 'cancer',
    'Лев' : 'leo',
    'Дева' : 'virgo',
    'Весы' : 'libra',
    'Скорпион' : 'scorpio',
    'Стрелец' : 'sagittarius',
    'Козерог' : 'capricorn',
    'Водолей' : 'aquarius',
    'Рыбы' : 'pisces'
}

url = 'https://horoscopes.rambler.ru/'

def get_goroscop(name):
    # Проверяем, есть ли имя в ассоциациях
    if name in associations:
        # Формируем URL для запроса
        req_url = url + associations[name] + '/'
        
        # Выполняем GET-запрос
        response = requests.get(req_url)
        
        # Проверяем успешность запроса
        if response.status_code == 200:
            # Парсим содержимое страницы
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем блок с нужными классами
            block = soup.find('p', class_='_5yHoW AjIPq')
            
            # Если блок найден, возвращаем его текст
            if block:
                return block.get_text()
            else:
                return 'Блок с указанными классами не найден.'
        else:
            return f'Ошибка при выполнении запроса: {response.status_code}'
    else:
        return 'Неверное имя. Проверьте правильность ввода.'