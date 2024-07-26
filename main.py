import base64
import io
from creditionals import *
from datetime import datetime
from flask import Flask, request
from SpeechToText import speech_to_text
from PIL import Image
from telebot import TeleBot
from Text2Image import Text2ImageAPI
from hangman import Hangman
from tic_tac_toe import TicTacToe
from akaneko import get_hentai

app = Flask(__name__)
bot = TeleBot(TOKEN)
hangman_game = Hangman()
tic_tac_toe = TicTacToe()

@bot.message_handler(commands=['start'])
def start(message):
    answer = f'Привет, {message.from_user.first_name} {message.from_user.last_name}!'
    bot.send_message(message.chat.id, text=answer, parse_mode='html')


@bot.message_handler(commands=['hentai'])
def hentai(message):
    pic_url = get_hentai()
    bot.send_photo(message.chat.id, photo=pic_url)


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
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
    else:
        markup = tic_tac_toe.generate_board_markup()
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)

    if result == "Позиция уже занята. Попробуйте другую.":
        bot.answer_callback_query(callback_query_id=call.id, text=result, show_alert=True)


@bot.message_handler(commands=['hangman'])
def hangman(message):
    if not hangman_game.game_on:
        hangman_game.start()
        text = f'Добро пожаловать в игру. Отгадай слово \n {hangman_game.info()}'
        bot.send_message(message.chat.id, text=text)
    if hangman_game.game_on:
        hangman_game.game_over()


@bot.message_handler(content_types=['voice'])
def voice(message):
    file = bot.get_file(message.voice.file_id)
    voice_bytes = bot.download_file(file.file_path)
    current_time = datetime.now().strftime('%H-%M-%S')
    filepath = f'voices/{message.chat.id.replace('~', '')}_{current_time}_voice-message.ogg'
    with open(filepath, 'wb') as f:
        f.write(voice_bytes)

    bot.reply_to(message, text=speech_to_text(filepath))


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


@bot.message_handler()
def on_message(message):
    if hangman_game.game_on:
        if len(message.text) > 1:
            bot.send_message(message.chat.id, 'Вводить можно только буквы!\n' + hangman_game.info())
        else:
            msg = hangman_game.game_step(message.text)
            bot.send_message(message.chat.id, text=msg)


if __name__ == '__main__':
    bot.polling(non_stop=True)
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + 'webhook')
    app.run(host='0.0.0.0', port=5000)
