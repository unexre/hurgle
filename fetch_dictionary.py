#!/usr/bin/python3

import re
import json
import random
import datetime

from urllib.request import urlopen

HURGLE_URL = "https://hurgle.me/"
TXT_FILE = "hurgle-me.txt.tmp"
JS_FILE = "answers.js.tmp"


def main():
    year = datetime.datetime.now().year

    # grab the main HTML file to locate the latest minified JS hash
    with urlopen(HURGLE_URL) as response:
        html = response.read()
    match = re.search(b"\/static\/js\/main\.\w+\.js", html)
    if not match:
        raise Exception("Could not find script name in source code.")

    # fetch the JS file
    js_url = HURGLE_URL + match.group(0).decode().strip("/")
    with urlopen(js_url) as response:
        js = response.read()

    matcher_answers = re.search(b"m,h,p=(\[.*\]),g=", js)
    matcher_dictionary = re.search(b'\],g=(\[.*\]),b="', js)

    # listify the wordlists
    live_word_list = json.loads(matcher_dictionary.group(1))
    live_answer_list = json.loads(matcher_answers.group(1))

    output_set = set()
    for w in live_word_list + live_answer_list:
        output_set.add(w.lower())

    txt_list = list(output_set)
    random.shuffle(txt_list)
    with open(TXT_FILE, "w") as f:
        f.write("\n".join(txt_list))

    js_list = {
        "2023": live_answer_list,
        "2024": [],
        "2025": [],
    }
    with open(JS_FILE, "w") as f:
        f.write("const answers = " + json.dumps(js_list, indent=2) + ";")

    print(
        "Successfully downloaded. Verify {} and {} look valid, then rename them to remove the .tmp extensions.".format(
            TXT_FILE, JS_FILE
        )
    )


if __name__ == "__main__":
    main()
