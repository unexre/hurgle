# hurgle

Guesser for Hurgle (and Wordle)

**This will not let you run Wordle or Hurgle. It is for cheaters who want to cheat.**

There is a Python script to help you guess more in a systematic method. That method is _not_ an optimal solver; it was just an exercise in writing a guessing algorithm.

There is a single-page webapp to let you see a single letter of today's word. I use this when playing fairly but get really stumped.

## Prerequisites

These tools do not require installing any packages or creating a virtualenv. If you don't have Python, you're on your own.

For copyright, ethical, up-to-dateness, and i-dont-want-to-anger-github reasons, this repository does not include a word dictionary, nor the actual answers the live version of the game. Before using either of these tools, you will need to obtain a dictionary (saved as `hurgle-me.txt`, one word per line in the style of `/usr/share/dict/words`) and the answers (saved as a JS object in `answers.js`).

**You only need to perform this step once. The output will be used by both tools.**

Run `./fetch_dictionary.py` in the root of this repository. It will fetch the game's source code, extract the valid word list and daily answer list, and dump those values into `hurgle-me.txt.tmp` and `answers.js.tmp`.

Check the `.tmp` files contain approximately-readable words. Don't actually read them, though. You'll spoil the game for yourself. Determining how to do this is an exercise left to the reader.

Rename the files to remove the `.tmp` extension, overwriting old files if necessary.

### For Wordle

If you plan to use this script for the real, live Wordle on the newspaper website, you should obtain a copy of TWL (or a similar Scrabble dictionary) from the Internet. `/usr/share/dict/words` on most systems is an incredibly out-of-date snapshot of Pre-WWII English vocabulary and is not a good choice for most word games. It can serve in a pinch. Either paste the contents of your chosen dictionary, one word per line, into `hurgle-me.txt` or create a symbolic link to another dictionary on your system. If the phrase "symbolic link" is new to you, please find other tools for cheating at games.

## Guesser Script

On any given day, run `./hurgle.py`. It will suggest guesses. After you submit the guess to Wordle/Hurgle, enter its response into the prompt. The guesser will suggest another word based on that. Repeat until done.

### Entering Responses

* Enter a **green** letter (correct position) in CAPS, e.g. `A`
* Enter a **yellow** letter (correct letter, incorrect position) in lowercase, e.g. `a`
* Enter a **grey** letter (unused letter) as `*`

Example: `dI*E*` (guess was DICEY, correct word was FINED)

## Spoiler Tool

If you just want to know a single letter without having the rest of today's word spoiled, try this single-page webapp. 

Open [static.html](static.html) in your browser, using File -> Open or something like that.

It will display gray boxes, one for each letter in today's word. Click on a box to reveal (or re-hide) that specific letter.

### Online Version

This is also hosted at `hurgle.<name of the developer>.me` if you don't want to download it from Github.
