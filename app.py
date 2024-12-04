import pathlib
import configparser
from flask import Flask, request
import telepot
from telepot.loop import OrderedWebhook

config_path = pathlib.Path(__file__).parent.absolute() / "settings.ini"
config = configparser.ConfigParser()
config.read(config_path)

secret = config["TOKEN"]["secret"]
url = config["URL"]["base"]
bot = telepot.Bot(config["TOKEN"]["bot"])

app = Flask(__name__)

webhook = OrderedWebhook(bot)

@app.route("/health-check")
def index():
    return "OK!"

@app.route("/{}".format(secret), methods=["GET", "POST"])
def webhook_handler():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        if "text" in update["message"]:
            text = update["message"]["text"]
            bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
        else:
            bot.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")
    return "OK"


if __name__ == "__main__":
    try:
        bot.setWebhook(url + "/{}".format(secret))
        # Sometimes it would raise this error, but webhook still set successfully.
    except telepot.exception.TooManyRequestsError:
        pass

    webhook.run_as_thread()
    app.run()
