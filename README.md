# Hangman Word Guessing Game (Console)

A terminal-based Hangman game written in Python 3 using only the standard library.

## Features
- Guess a hidden word letter by letter with **6 allowed mistakes**
- ASCII gallows art that updates after every wrong guess
- Shows the masked word (e.g. `p _ t h _ n`) and all wrong letters guessed
- Repeated guesses are detected and **do not cost an attempt**
- Input validation (only single letters a-z accepted)
- Clear victory and game-over screens
- Play-again option with a running win/loss score
- Uses `word.txt` if present, otherwise a built-in word list

## Requirements
- Python 3.6 or newer
- No external libraries (uses only `random` and `os`)

## How to Run
1. Put `hangman.py` in a folder.
2. (Optional) Download the English words list and save it as `word.txt` in the same folder.
3. Open a terminal in that folder and run:

```
python hangman.py
```

(On some systems use `python3 hangman.py`.)

## How to Play
1. The game shows blanks for each letter of the secret word.
2. Type one letter and press Enter.
3. Correct letter: it is revealed in the word.
4. Wrong letter: another part of the hangman is drawn.
5. Win by revealing the whole word; lose after 6 wrong guesses.
6. Type `y` at the end to play again.

## Sample Output
```
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========

Word: p _ t _ _ n
Wrong letters: x z
Attempts left: 4

Guess a letter:
```

## Project Structure
```
hangman.py              # the game
word.txt                # optional word list (one word per line)
README.md               # this file
Hangman_Explanation.md  # detailed explanation of the code
```

## Code Overview
| Function | Purpose |
|---|---|
| `load_words()` | Loads words from `word.txt` or the built-in list |
| `mask_word()` | Builds the hidden-word display |
| `show_status()` | Prints gallows, word, wrong letters, attempts left |
| `get_guess()` | Validates input and rejects duplicate guesses |
| `play_round()` | Runs one complete game |
| `main()` | Handles scoring and the play-again loop |
