from random import choice

ERRORS = (
    """
   _______
  |/
  |
  |
  |
  |
  |
  |
__|________
|         |
""",
    """
   _______
  |/
  |     ( )
  |
  |
  |
  |
  |
__|________
|         |
""",
    """
   _______
  |/
  |     ( )
  |      |
  |
  |
  |
  |
__|________
|         |
""",
    """
   _______
  |/
  |     ( )
  |      |_
  |        \\
  |
  |
  |
__|________
|         |
""",
    """
   _______
  |/
  |     ( )
  |     _|_
  |    /   \\
  |
  |
  |
__|________
|         |
""",
    """
    _______
  |/
  |     ( )
  |     _|_
  |    / | \\
  |      |
  |
  |
__|________
|         |
""",
    """
   _______
  |/
  |     ( )
  |     _|_
  |    / | \\
  |      |
  |     / \\
  |    /   \\
__|________
|         |
""",
    """
    _______
  |/     |
  |     (_)
  |     _|_
  |    / | \\
  |      |
  |     / \\
  |    /   \\
__|________
|         |
"""
)

with open('words.txt', 'r', encoding='utf-8') as file:
    WORDS = [line.strip().lower() for line in file.readlines()]


class Hangman:
    def __init__(self):
        self.used = []
        self.word = choice(WORDS)
        self.so_far = ['_'] * len(self.word)
        self.wrong = 0
        self.game_on = False
        self.max_wrong = len(ERRORS) - 1

    def start(self):
        self.game_on = True

    def info(self):
        msg = ERRORS[self.wrong]
        msg += "\n Вы использовали следующие буквы: \n"
        msg += str(self.used) + '\n'
        msg += ' '.join(self.so_far)
        msg += '\n\n Введите новую букву'
        return msg

    def game_step(self, letter):
        letter = letter.lower()
        if letter in self.used:
            return 'Буква уже была использована'
        else:
            self.used.append(letter)
            if letter in self.word:
                msg = f'\n Буква {letter} есть в слове!\n'
                indxs = [i for i in range(len(self.word)) if self.word[i] == letter]
                for indx in indxs:
                    self.so_far[indx] = letter
                if self.so_far.count('_') == 0:
                    msg = f'Вы победили. Загаданное слово: {self.word}'
                    self.game_over()
                else:
                    msg += self.info()
            else:
                msg = f'\n Такой буквы нет в слове \n'
                self.wrong += 1
                if self.wrong >= self.max_wrong:
                    msg += ERRORS[self.max_wrong]
                    msg += f'\n Вас повесили.\nСлово было {self.word}'
                    self.game_over()
                else:
                    msg += self.info()
            return msg

    def game_over(self):
        self.used = []
        self.game_on = False
        self.word = choice(WORDS)
        self.so_far = ['_'] * len(self.word)
        self.wrong = 0
        self.game_on = False
        self.max_wrong = len(ERRORS) - 1