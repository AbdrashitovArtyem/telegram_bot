import base64
import io
import random
import threading
import requests
from creditionals import TOKEN
from datetime import datetime
from flask import Flask, request
from SpeechToText import speech_to_text
from PIL import Image
from telebot import TeleBot, types
import os
import html
from goroscop import get_goroscop
from random_fact import get_fact
from Text2Image import Text2ImageAPI
# from hangman import Hangman
from tic_tac_toe import TicTacToe
from GetWether import get_weather
from akaneko import get_hentai
from recipe import get_random_meal

app = Flask(__name__)
bot = TeleBot(TOKEN)
# hangman_game = Hangman()
tic_tac_toe = TicTacToe()

def count_files_in_folder(folder_path):
    return len([entry for entry in os.scandir(folder_path) if entry.is_file()])

@app.route('/webhook', methods=['POST'])
def webhook():
    print("Webhook received")  # Лог для отладки
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Unsupported Media Type', 415

@bot.message_handler(commands=['start'])
def start(message):
    answer = f'Привет, {message.from_user.first_name} {message.from_user.last_name}!'
    bot.send_message(message.chat.id, text=answer, parse_mode='html')

@bot.message_handler(commands=['denis'])
def denis(message):
    try:
        folder_path = '/var/www/telegram_bot/denis'
        count_files = count_files_in_folder(folder_path)

        if count_files > 0:
            random_index = random.randint(0, count_files - 1)  # Укажите точное количество файлов, если известно
            selected_image = None
            
            with os.scandir(folder_path) as entries:
                for i, entry in enumerate(entries):
                    if i == random_index:
                        selected_image = entry.path
                        break
            if selected_image:
                with open(selected_image, 'rb') as img:
                    sent_message = bot.send_photo(message.chat.id, img)
                    threading.Timer(30, delete_message, args=[message.chat.id, sent_message.message_id]).start()
                    threading.Timer(30, delete_message, args=[message.chat.id, message.message_id]).start()
            else:
                bot.send_message(message.chat.id, 'Изображение не найдено.')
        else:
            bot.send_message(message.chat.id, 'В папке нет изображений.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка: {str(e)}')

@bot.message_handler(content_types=['voice'])
def voice(message):
    file = bot.get_file(message.voice.file_id)
    voice_bytes = bot.download_file(file.file_path)
    current_time = datetime.now().strftime('%H-%M-%S')
    filepath = f'/var/www/telegram_bot/voices/{current_time}_voice-message.ogg'
    with open(filepath, 'wb') as f:
        f.write(voice_bytes)
    bot.reply_to(message, text=speech_to_text(filepath))

@bot.message_handler(content_types=['video_note'])
def voice(message):
    file = bot.get_file(message.video_note.file_id)
    voice_bytes = bot.download_file(file.file_path)
    current_time = datetime.now().strftime('%H-%M-%S')
    filepath = f'/var/www/telegram_bot/video_notes/{current_time}-video_note-message.mp4'
    with open(filepath, 'wb') as f:
        f.write(voice_bytes)
    bot.reply_to(message, text=speech_to_text(filepath))

# Указываем путь к папке для сохранения изображений
hentai_folder = "hentai"

# Создаем папку, если она не существует
if not os.path.exists(hentai_folder):
    os.makedirs(hentai_folder)

@bot.message_handler(commands=['hentai'])
def hentai(message):
    pic_url = get_hentai()  # Получаем URL картинки
    response = requests.head(pic_url)  # Получаем заголовки файла

    content_type = response.headers.get('Content-Type')  # Извлекаем Content-Type

    if 'gif' in content_type:
        # Если это GIF, отправляем как видео
        sent_message = bot.send_video(message.chat.id, pic_url, None)
    else:
        # В противном случае отправляем как фото
        sent_message = bot.send_photo(message.chat.id, photo=pic_url)

    save_image(pic_url)  # Сохраняем изображение
    
    # Устанавливаем таймеры на удаление сообщений через 60 секунд
    threading.Timer(30, delete_message, args=[message.chat.id, sent_message.message_id]).start()
    threading.Timer(30, delete_message, args=[message.chat.id, message.message_id]).start()

def save_image(pic_url):
    hentai_folder = "hentai"

    # Создаем папку, если она не существует
    if not os.path.exists("hentai"):
        os.makedirs(hentai_folder)
    # Получаем имя файла из URL
    file_name = os.path.join(hentai_folder, os.path.basename(pic_url))
    
    # Скачиваем изображение
    response = requests.get(pic_url)
    
    # Сохраняем изображение в файл
    with open(file_name, 'wb') as f:
        f.write(response.content)

def delete_message(chat_id, message_id):
    bot.delete_message(chat_id, message_id)

def clean_html(html_text):
    # Заменяем <br> на перенос строки
    html_text = html_text.replace('<br>', '\n')
    # Удаляем другие неподдерживаемые теги, если есть
    html_text = re.sub(r'<[^>]+>', '', html_text)
    return html_text

@bot.message_handler(commands=['recipe'])
def recipe(message):
    bot.send_message(message.chat.id, text='Сейчас подыщем что-нибудь для тебя')
    
    meal_data = get_random_meal()
    
    if 'error' in meal_data:
        bot.reply_to(message, meal_data['error'])
    else:
        recipe_caption = (
            f"*{meal_data['name']}*\n\n"
            f"*Ингредиенты:*\n{meal_data['ingredients']}\n\n"
            f"*Инструкция:*\n{meal_data['instructions']}"
        )
        bot.send_photo(
            chat_id=message.chat.id,
            photo=meal_data['image'],
            caption=recipe_caption,
            parse_mode='Markdown'
        )

@bot.message_handler(commands=['weather'])
def send_weather(message):
    try:
        city = message.text.split(maxsplit=1)[1]
        weather_info = get_weather(city)
        bot.reply_to(message, weather_info)
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите город после команды /weather.")

@bot.message_handler(commands=['fact'])
def fact(message):
    bot.send_message(message.chat.id, get_fact())

@bot.message_handler(commands=['goroscop'])
def goroscop(message):
    try:
        name = message.text.split(maxsplit=1)[1]
        goroscop_info = get_goroscop(name)
        bot.reply_to(message, goroscop_info)
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите знак зодиака после команды /weather.")

@bot.message_handler(commands=['tictactoe'])
def tictactoe(message):
    tic_tac_toe.start_game()
    text = "Привет, сыграем в крестики-нолики?"
    markup = tic_tac_toe.generate_board_markup()
    bot.send_message(message.chat.id, text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('move_'))
def handle_move(call):
    index = int(call.data.split('_')[1])
    result = tic_tac_toe.game_step(index)

    if result:
        bot.send_message(call.message.chat.id, text=result)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    else:
        markup = tic_tac_toe.generate_board_markup()
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

    if result == "Позиция уже занята. Попробуйте другую.":
        bot.answer_callback_query(callback_query_id=call.id, text=result, show_alert=True)

# @bot.message_handler(commands=['hangman'])
# def hangman(message):
#     if hangman_game.game_on:
#         print('Сюда не заходит')
#         hangman_game.game_over()
#         text = f'Игра виселица остановлена'
#     else:
#         hangman_game.start()
#         text = f'Добро пожаловать в игру. Отгадай слово \n {hangman_game.info()}'
#         bot.send_message(message.chat.id, text=text)


@bot.message_handler(commands=['anime'])
def anime(message):
    try:
        prompt = message.text[len('/anime '):].strip()
        if prompt == 'just_developer_bot':
            return
        if not prompt:
            bot.send_message(message.chat.id, "Пожалуйста, укажите описание для генерации изображения.")
            return
        print(f"Запрос на генерацию от пользователя {message.from_user.username}: {prompt}")
        api = Text2ImageAPI()
        model_id = api.get_model()
        if not model_id:
            bot.send_message(message.chat.id, "Не удалось получить модель для генерации изображения.")
            return
        print(f'model_id: {model_id}')
        uuid = api.generate(prompt, model_id)
        if not uuid:
            bot.send_message(message.chat.id, "Не удалось сгенерировать изображение. Попробуйте позже.")
            return
        print(f'uuid: {uuid}')
        images = api.check_generation(uuid)
        if not images:
            bot.send_message(message.chat.id, "Изображения не удалось сгенерировать. Попробуйте позже.")
            return
        print('Картинка сгенерирована')
        for img_data in images:
            try:
                img_bytes = base64.b64decode(img_data)
                img = Image.open(io.BytesIO(img_bytes))
                bio = io.BytesIO()
                bio.name = 'image.jpeg'
                img.save(bio, 'JPEG')
                bio.seek(0)
                bot.send_photo(message.chat.id, photo=bio, caption=prompt)
            except Exception as e:
                print(f"Ошибка при обработке изображения: {e}")
                bot.send_message(message.chat.id, "Ошибка при обработке изображения. Попробуйте позже.")
    except Exception as e:
        print(f"Ошибка в команде /anime: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при выполнении команды. Попробуйте позже.")

# @bot.message_handler()
# def on_message(message):
#     if hangman_game.game_on:
#         if len(message.text) > 1:
#             bot.send_message(message.chat.id, 'Вводить можно только буквы!\n' + hangman_game.info())
#         else:
#             msg = hangman_game.game_step(message.text)
#             bot.send_message(message.chat.id, text=msg)

def setup_webhook():
    webhook_url = 'https://just-developer.ru/webhook'
    bot.remove_webhook()
    success = bot.set_webhook(url=webhook_url)
    if success:
        print(f"Webhook set successfully: {webhook_url}")
    else:
        print("Failed to set webhook")

if __name__ == '__main__':
    setup_webhook()
    app.run(host='0.0.0.0', port=5000)
