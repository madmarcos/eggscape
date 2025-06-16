import random
from enum import Enum

CHOICE_EXIT = 2

class GameStatus(Enum):
    INACTIVE = 0
    WIN = 1
    LOSE = 2
    GUESS_HIGH = 3
    GUESS_LOW = 4
    RUNNING = 5

class GameData:
    def __init__(self):
        self.answer = None
        self.num_guesses = 0
        self.max_guesses = 3
        self.guess_range_min = None
        self.guess_range_max = None
        self.game_status = GameStatus.INACTIVE

def get_number(guess_min, guess_max):
    while True:
        try:
            test_guess = input(f"Enter a number between {guess_min} and {guess_max}: ")
            guess = int(test_guess)
            if guess < guess_min or guess > guess_max:
                print(f"Please enter a whole number within {guess_min} and {guess_max}.")
                continue
            return guess
        except ValueError:
            print("Please enter a whole number!")
            continue

class NumberGuesser:
    def __init__(self, name, guess_min, guess_max, max_guesses):
        self.name = name
        self.game_data = GameData()
        self.game_data.guess_range_min = guess_min
        self.game_data.guess_range_max = guess_max
        self.game_data.max_guesses = max_guesses

    def init_game(self):
        # reset the per-game data
        self.game_data.answer = random.randint(self.game_data.guess_range_min, self.game_data.guess_range_max)
        self.game_data.num_guesses = 0
        self.game_data.game_status = GameStatus.RUNNING

    def process_input(self):
        """
        gets input from user and changes game status accordingly

        :return: nothing
        """
        self.game_data.num_guesses += 1
        guess = get_number(self.game_data.guess_range_min, self.game_data.guess_range_max)

        if guess == self.game_data.answer:
            self.game_data.game_status = GameStatus.WIN
            return

        if self.game_data.num_guesses == self.game_data.max_guesses:
            self.game_data.game_status = GameStatus.LOSE
            return

        # else player guessed too high or too low
        if guess < self.game_data.answer:
            self.game_data.game_status = GameStatus.GUESS_LOW
        else:
            self.game_data.game_status = GameStatus.GUESS_HIGH

    def render(self):
        match self.game_data.game_status:
            case GameStatus.GUESS_LOW:
                print(f'Too low!')
                self.game_data.game_status = GameStatus.RUNNING
            case GameStatus.GUESS_HIGH:
                print(f'Too high!')
                self.game_data.game_status = GameStatus.RUNNING
            case GameStatus.WIN:
                print(f'You WIN!')
            case GameStatus.LOSE:
                print(f'Loser!!')
            case _:
                print(f"Unknown game status {self.game_data.game_status}")

    def play_game(self):
        self.init_game()

        print(f'Let\'s play guess the number.')

        try:
            while self.game_data.game_status == GameStatus.RUNNING:
                self.process_input()
                self.render()

            print(f"It took you {self.game_data.num_guesses} guess{'es' if self.game_data.num_guesses > 1 else ''}.")
        except KeyboardInterrupt:
            print(f"Oh no! Something went wrong. :(")

    def show_menu(self):
        print(f'Welcome {self.name}!')
        print(f'Press 1 to play Number Guesser.')
        print(f'Press 2 to quit.')

    def process_menu_choice(self, choice):
        if choice == 1:
            self.play_game()

    def do_menu(self):
        while True:
            self.show_menu()
            choice = get_number(1, CHOICE_EXIT)
            if choice == CHOICE_EXIT:
                break
            self.process_menu_choice(choice)


if __name__ == "__main__":
    user_name = 'bob'
    #user_name = input("Enter your name: ")
    theApp = NumberGuesser(user_name, 1, 10, 3)
    theApp.do_menu()
