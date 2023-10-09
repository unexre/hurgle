#!/usr/bin/python3

import re
import sys
import random
import datetime

CAPS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWS = "abcdefghijklmnopqrstuvwxyz"

STRINGS = {
    "instructions": {
        "en": """
  Enter a green letter (correct position) in CAPS
  Enter a yellow letter (correct letter, incorrect position) in lowercase
  Enter a grey letter (unused letter) as *

  Example:  dI*E*   (guess was DICEY, correct word was FINED)
""",
    },
    "turn_prompt": {
        "en": "Enter the result, ! to end, - to reject, ? for formatting help, % for the list: ",
    },
    "play_again": {
        "en": "Play again? [Y/n] ",
    },
    "get_length": {
        "en": "Number of letters in the game (3-10, default {0}): ",
    },
    "one_left": {
        "en": "** Only one word remains: {0}",
    },
    "suggest_guess": {
        "en": "** {0} words left. Try this: {1}",
    },
    "goodbye": {
        "en": "\n\nGoodbye.",
    },
    "too_many": {
        "en": "!! Looks like you made more guesses than the game allows, but we will keep going.",
    },
    "initialized": {
        "en": "!! Loaded {0} words."
    },
    "word_list": {
        "en": "Remaining candidates: \n   {0}",
    },
    "error_result": {
        "en": "-- Bad input, ignoring.",
    },
    "error_mismatch": {
        "en": "-- Response does not match suggested guess, ignoring. Use & to replace the guess.",
    },
    "pruned": {
        "en": "Done pruning. Pruned {0}.",
    },
    "noop": {
        "en": "Input not processed, nothing pruned.",
    },
    "error_oow": {
        "en": "** No candidate words, we are in trouble.",
    },
    "restart": {
        "en": "Starting over!",
    },
    "replace_guess": {
        "en": "Enter the word you want to guess instead: ",
    },
    "error_guess_unknown": {
        "en": "That word is not among the remaining candidate words.",
    },
}

RULESETS = {
    "hurgle": {
        "dict": "hurgle-me.txt",
        "freq": {
            "e": 3, "a": 3, "s": 3, "r": 3, "i": 3, "n": 3, "o": 3, "l": 3, "t": 2,
            "u": 2, "d": 2, "c": 2, "m": 2, "h": 2, "p": 2, "g": 2, "b": 2, "y": 2,
            "k": 2, "f": 2, "w": 2, "v": 1, "z": 1, "j": 1, "x": 1, "q": 1,
        },
        "first_guesses": ["loaner", "oilers", "aliens", "reason", "sailor",],
    },
    "wordle": {
        # NYI
        "dict": "wordlist.txt",
        "freq": None,
        "first_guesses": None,
    }
}


def iloc(str_id, newline=False, params=[]):
    prompt = STRINGS[str_id][lang].format(*params)
    if newline:
        print(prompt, flush=True)
    else:
        print(prompt, end="", flush=True)

    return sys.stdin.readline().strip()


def ploc(str_id, newline=True, params=[]):
    message = STRINGS[str_id][lang].format(*params)
    if newline:
        print(message, flush=True)
    else:
        print(message, end="", flush=True)


class GuessGame(object):
    LENGTH_MIN = 3
    LENGTH_MAX = 10
    LENGTH_DEFAULT = 6 if datetime.datetime.now().year == 2023 else 7

    def __init__(self, length=-1, rules=""):
        if (length < self.LENGTH_MIN) or length > self.LENGTH_MAX:
            self.length = self.LENGTH_DEFAULT
        else:
            self.length = length

        if rules not in RULESETS:
            rules = "hurgle"
        self.rule_freq = RULESETS[rules]["freq"]
        self.rule_first_guesses = RULESETS[rules]["first_guesses"]
        self.rule_dict = RULESETS[rules]["dict"]

        re_valid = f"^[A-Za-z*]{{{self.length}}}$"
        self.validator = re.compile(re_valid)

        self.words = list()  # don't modify this

        self.candidates = set()  # will contain dynamic subset of self.words
        self.guess = None
        self.next_guess = None
        self.result = None
        self.known_bad = set()
        self.known_good = set()

        self.load_words()

    def load_words(self):
        from os.path import exists

        try_these_files = [
            self.rule_dict,
            "/usr/share/dict/words",
            "wordlist.txt"
        ]
        filename = next(fn for fn in try_these_files if exists(fn))
        with open(filename) as fh:
            for word in fh.readlines():
                word = word.strip().lower()
                if len(word) == self.length:
                    self.words.append(word)
        ploc("initialized", params=[len(self.words),])

    @property
    def is_active(self):
        return self.guess is not None

    def get_next_highest(self):
        if self.next_guess:
            next_guess = self.next_guess
            self.next_guess = None
            return next_guess

        # start() seeds guess with "*****", so handle first turn specially
        if "*" in self.guess and len(self.rule_first_guesses) > 0:
            # fixme: if a value in first_guesses is not in candidates, things might go badly?
            #   Do a loop here until they're all exhausted and/or pre-prune these and skip if len=0
            return random.choice(self.rule_first_guesses)

        high_score = 0
        high_word = "broken"

        for w in self.candidates:
            score = 0
            for x in set(w):
                score += 0 if x in self.known_good else self.rule_freq[x]
            # print(f"{w} scored {score}")
            if score > high_score:
                high_score = score
                high_word = w

        # print(f"High score was {high_score} for {high_word}")

        return high_word

    def process_input(self, new_result):
        if len(new_result) == 0:
            self.result = None
            return

        if new_result[0] in "?!-%&":
            action = new_result[0]
            self.result = None
            if action == "!":
                # quit
                self.end()
            if action == "?":
                # help
                ploc("instructions")
            if action == "-":
                # skip the suggested guess
                self.candidates.discard(self.guess)
                ploc("pruned", params=[self.guess])
            if action == "%":
                # print remaining word list
                word_list = "\n   ".join(self.candidates)
                ploc("word_list", params=[word_list,])
            if action == "&":
                # replace self.guess with user-supplied word
                new_guess = iloc("replace_guess")
                while new_guess not in self.candidates:
                    ploc("error_guess_unknown")
                    new_guess = iloc("replace_guess")
                self.next_guess = new_guess
            return

        # entered something really unexpected?
        if len(new_result) != self.length or not self.validator.match(new_result):
            # print(f"new_result = {new_result}")
            # print(f"self.length = {self.length}")
            # print(f"len(result) = {len(new_result)}")
            # print(f"validator = {self.validator}")
            ploc("error_result")
            self.result = None
            return

        # entered a wordle clue that is not consistent with the suggested guess?
        checker = new_result.replace("*", ".").lower()
        if not re.match(checker, self.guess):
            ploc("error_mismatch")
            self.result = None
            return

        # at this point we're pretty sure we made a valid guess
        self.result = new_result

    def make_guess(self):
        if self.result:
            must = "^"
            suspected_bad = set()
            bonus_filter = list()

            for position, letter in enumerate(self.result):
                if letter in LOWS:
                    must += "."
                    self.known_good.add(letter)
                    bonus_filter.append(
                        "^"
                        + "." * position
                        + letter
                        + "." * (self.length - position - 1)
                        + "$"
                    )
                    # todo: if there's only one * left and only one lowercase left, this letter MUST be there
                    continue
                if letter in CAPS:
                    must += letter.lower()
                    self.known_good.add(letter.lower())
                    continue
                if letter == "*":
                    must += "."
                    if self.guess[position] in self.known_good:
                        bonus_filter.append(
                            "^"
                            + "." * position
                            + self.guess[position]
                            + "." * (self.length - position - 1)
                            + "$"
                        )
                    else:
                        qwert = self.guess[position]
                        suspected_bad.add(qwert)
                        # print(f"Added {qwert} to suspected_bad")
                    continue

            suspected_bad = suspected_bad - set("*")  # just in case it made it in
            self.known_bad = suspected_bad - self.known_good
            # print(f"known bad looks like {self.known_bad}")

            must += "$"

            re_must = re.compile(must)

            prunes = set()
            for w in self.candidates:
                if not re_must.match(w):
                    prunes.add(w)

                if w not in prunes:
                    for bad in self.known_bad:
                        if bad in w:
                            prunes.add(w)
                            break

                if w not in prunes:
                    for good in self.known_good:
                        if good not in w:
                            prunes.add(w)
                            break

                if w not in prunes:
                    for bonus in bonus_filter:
                        if re.match(bonus, w):
                            prunes.add(w)
                            break

            for p in prunes:
                self.candidates.discard(p)

            ploc("pruned", params=[len(prunes)])

        if len(self.candidates) == 0:
            ploc("error_oow")
            self.end()
            return

        if len(self.candidates) == 1:
            ploc("one_left", params=[list(self.candidates)[0],])
            self.end()
            return

        self.guess = self.get_next_highest()

        ploc("suggest_guess", params=[len(self.candidates), self.guess])

    def start(self):
        self.guess = "*" * self.length
        self.result = None
        self.known_bad.clear()
        self.known_good.clear()
        self.candidates = set(self.words[:])

    def end(self):
        again = iloc("play_again").lower()

        if "n" in again:
            raise KeyboardInterrupt
        else:
            ploc("restart")
            self.start()
            self.make_guess()


def main():
    try:
        try:
            game_length = int(iloc("get_length", params=[GuessGame.LENGTH_DEFAULT]))
        except ValueError as e:
            game_length = GuessGame.LENGTH_DEFAULT

        game = GuessGame(game_length, rules=rules)
        game.start()

        while True:
            game.make_guess()
            player_input = iloc("turn_prompt")
            game.process_input(player_input)
    except (KeyboardInterrupt, EOFError) as e:
        ploc("goodbye", newline=True)
        sys.exit()


if __name__ == "__main__":
    lang = "en"
    rules = "hurgle"
    main()
