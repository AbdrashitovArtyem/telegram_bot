import requests

def get_weather(city):
    # Получаем координаты города с помощью API Open-Meteo (или другого геокодинг-сервиса)
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru"
    geocode_response = requests.get(geocode_url)
    geocode_data = geocode_response.json()

    if geocode_data['results']:
        latitude = geocode_data['results'][0]['latitude']
        longitude = geocode_data['results'][0]['longitude']
        city_name = geocode_data['results'][0]['name']

        # Получаем прогноз погоды для полученных координат
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&timezone=Europe/Yekaterinburg"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        if 'current_weather' in weather_data:
            temperature = weather_data['current_weather']['temperature']
            windspeed = weather_data['current_weather']['windspeed']
            weather_info = (
                f"Погода в городе {city_name}:\n"
                f"Температура: {temperature}°C\n"
                f"Скорость ветра: {windspeed} м/с"
            )
            return weather_info
        else:
            return "Не удалось получить данные о погоде."
    else:
        return "Не удалось найти такой город. Проверьте правильность названия."