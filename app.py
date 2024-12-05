import pathlib
import urllib3
import configparser
from flask import Flask, request
import telepot
from telepot.loop import OrderedWebhook

from bot.brain import Brain

config_path = pathlib.Path(__file__).parent.absolute() / "settings.ini"
config = configparser.ConfigParser()
config.read(config_path)

secret = config["TOKEN"]["secret"]
url = config["URL"]["base"]

brain = Brain(config)

app = Flask(__name__)

proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

bot = telepot.Bot(config["TOKEN"]["bot"])
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

            answer = brain.handle_answer(text)

            bot.sendMessage(chat_id, "{}".format(answer))
    return "OK"


@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    try:
        bot.setWebhook(url + "/{}".format(secret))
        return "OK"
    except telepot.exception.TooManyRequestsError:
        return "FALSE"


if __name__ == "__main__":
    webhook.run_as_thread()
    app.run()
