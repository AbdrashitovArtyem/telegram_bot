from telebot import types


WIN_COMBINATIONS = (
    # По горизонтали
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    # По вертикали
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    # По диагонали
    (0, 4, 8),
    (2, 4, 6),
)


class TicTacToe:
    def __init__(self):
        self.game_on = False
        self.game_board = ['*'] * 9
        self.player = "X"

    def start_game(self):
        self.game_on = True
        self.game_board = ['*'] * 9
        self.player = "X"

    def end_game(self):
        self.game_on = False
        self.game_board = ['*'] * 9
        self.player = "X"

    def game_step(self, index):
        if not self.game_on:
            return "Игра не началась. Начните игру командой /tictactoe."

        if self.game_board[index] != '*':
            return "Позиция уже занята. Попробуйте другую."

        self.game_board[index] = self.player

        if self.check_win():
            return f"Игрок {self.player} победил!"
        elif '*' not in self.game_board:
            return "Ничья!"

        self.player = "O" if self.player == "X" else "X"
        return None

    def check_win(self):
        for combo in WIN_COMBINATIONS:
            if self.game_board[combo[0]] == self.game_board[combo[1]] == self.game_board[combo[2]] != '*':
                return True
        return False

    def generate_board_markup(self):
        markup = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text=cell, callback_data=f"move_{i}") for i, cell in
                   enumerate(self.game_board)]

        for i in range(0, 9, 3):
            markup.row(*buttons[i:i + 3])
        return markup
