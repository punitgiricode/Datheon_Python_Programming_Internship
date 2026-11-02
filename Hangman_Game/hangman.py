"""
Hangman Word Guessing Game (Console)
------------------------------------
Guess the hidden word one letter at a time. You get 6 wrong guesses.
Repeated guesses are NOT penalised.

Run:  python hangman.py
Optional: put a file called words.txt (one word per line) next to this
script and the game will pick words from it instead of the built-in list.
"""

import os
import random

MAX_MISTAKES = 6

# ASCII gallows art: index = number of wrong guesses (0..6)
STAGES = [
    """
      +---+
      |   |
          |
          |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
     /    |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========
    """,
]

# Fallback list used when words.txt is not available
BUILT_IN_WORDS = [
    "python", "variable", "function", "keyboard", "algorithm", "compiler",
    "database", "network", "program", "software", "hardware", "internet",
    "terminal", "library", "iterator", "boolean", "integer", "console",
    "developer", "debugging", "recursion", "template", "browser", "pointer",
    "elephant", "mountain", "chocolate", "adventure", "umbrella", "triangle",
]


def load_words():
    """Load words from words.txt if it exists, otherwise use the built-in list."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "word.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            words = [w.strip().lower() for w in f if w.strip().isalpha() and len(w.strip()) >= 4]
        if words:
            return words
    return BUILT_IN_WORDS


def mask_word(secret, correct_letters):
    """Return the word with unguessed letters hidden, e.g. 'p _ t h _ n'."""
    return " ".join(ch if ch in correct_letters else "_" for ch in secret)


def show_status(secret, correct_letters, wrong_letters):
    """Print the gallows, the masked word and the guessed letters."""
    print(STAGES[len(wrong_letters)])
    print("Word:", mask_word(secret, correct_letters))
    print("Wrong letters:", " ".join(sorted(wrong_letters)) or "-")
    print("Attempts left:", MAX_MISTAKES - len(wrong_letters))
    print()


def get_guess(correct_letters, wrong_letters):
    """Ask until the player enters a valid, NEW single letter."""
    while True:
        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter (a-z).")
        elif guess in correct_letters or guess in wrong_letters:
            print(f"You already guessed '{guess}'. Try a different letter (no penalty).")
        else:
            return guess


def play_round(words):
    """Play one full game. Returns True if the player won."""
    secret = random.choice(words)
    correct_letters = set()
    wrong_letters = set()

    print("\n" + "=" * 40)
    print("        H A N G M A N")
    print("=" * 40)

    while True:
        show_status(secret, correct_letters, wrong_letters)

        # Win check: every letter of the secret has been guessed
        if set(secret) <= correct_letters:
            print("*" * 40)
            print(f"  VICTORY! You guessed the word: {secret.upper()}")
            print("*" * 40)
            return True

        # Lose check
        if len(wrong_letters) >= MAX_MISTAKES:
            print("x" * 40)
            print(f"  GAME OVER! The word was: {secret.upper()}")
            print("x" * 40)
            return False

        guess = get_guess(correct_letters, wrong_letters)

        if guess in secret:
            correct_letters.add(guess)
            print(f"Good guess! '{guess}' is in the word.\n")
        else:
            wrong_letters.add(guess)
            print(f"Sorry, '{guess}' is not in the word.\n")


def main():
    words = load_words()
    wins = losses = 0

    while True:
        if play_round(words):
            wins += 1
        else:
            losses += 1
        print(f"\nScore -> Wins: {wins} | Losses: {losses}")

        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing. Goodbye!")
            break


if __name__ == "__main__":
    main()
