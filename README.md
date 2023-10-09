# hurgle

Guesser for Hurgle (and Wordle)

## Guesser Script

These scripts do not require installing any packages or creating a virtualenv. If you don't have Python, you're on your own.

1. Populate the list of words.  You can create `hurgle-me.txt` from a source like `/usr/share/dict/words` or maybe a Scr%bble dictionary you found online, but the best way is to use Hurgle's own dictionary.  Copy it out of the source and paste it into the text file (caution: you'll probably see all the answers if you do this, since they are prominent in the source) **OR** run `./word_maker.py` once to fetch the game's source code, extract the list, and dump it into the right text file.  **Whichever method you choose, you only need to perform this step once.**

    * For the real live Wordle you'll probably want to find a copy of TWL out on the internet somewhere and use that.

2. Run `python3 hurgle.py` or `./hurgle.py`. It will suggest guesses. After you submit the guess to Wordle/Hurgle, enter its response into the prompt. The guesser will suggest another word based on that. Repeat until done.

### Entering Responses

* Enter a **green** letter (correct position) in CAPS, e.g. `A`
* Enter a **yellow** letter (correct letter, incorrect position) in lowercase, e.g. `a`
* Enter a **grey** letter (unused letter) as `*`

Example: `dI*E*` (guess was DICEY, correct word was FINED)

## Spoiler Tool

If you just want to know a single letter without having the rest of today's word spoiled, try this single-page webapp. 

1. Run `./word_maker.py` once to fetch the game's source code, extract the word list, and dump it into `ansers.js`.  **You only need to perform this step once. If you ran it for the guesser script, you do not need to run it again.**

2. Load [static.html](static.html) in your browser, using File -> Open or something like that.

It will display gray boxes, one for each letter in today's word. Click on a box to reveal (or re-hide) that specific letter.

### Online Version

This is also hosted at `hurgle.<name of the developer>.me` if you don't want to download it from Github.
