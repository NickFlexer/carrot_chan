import re
import configparser
import requests


class Brain:
    def __init__(self, config):
        self.bible_pattern = config["PATTERNS"]["bible"]

    def handle_answer(self, text):
        find_bible = re.search(self.bible_pattern, text)

        if find_bible:
            return self._bible()


    def _bible(self):
        bible_url = "https://justbible.ru/api/random?translation=rst"

        answer = "Такого в Писании нет"

        try:
            response = requests.get(bible_url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as er:
            answer = "Про это в Писании ничего нет"

        if response:
            answer = response.json()

        if answer.get("verse"):
            return answer["verse"].capitalize() + "(" + answer["info"] + ")"
        else:
            return answer


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("../settings.ini")
    brain = Brain(config)
    print(brain.handle_answer("Есть об этом что-то в библии?"))
