import logging
import logging.config
import os
import time
from typing import Dict

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
PRAKTIKUM_TOKEN = os.environ["PRAKTIKUM_TOKEN"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
PRAKTIKUM_API_URL = os.environ["PRAKTIKUM_API_URL"]

CHECKING_TIME = 300

logging.config.fileConfig("logging.ini")
logger = logging.getLogger()


def check_api_for_mandatory(new_homework):
    statuses_list = ["rejected", "reviewed", "approved"]
    homework = new_homework.get("homeworks")[0]
    checking_list = [
        isinstance(int(new_homework.get("current_date")), int),
        homework,
        homework.get("homework_name"),
        homework.get("status") in statuses_list,
    ]
    is_list_true = all(checking_list)
    if not is_list_true:
        if new_homework.get("error"):
            logger.error("Api returned error")
            raise Exception("Api returned error")
    logger.debug(f"checking api list returned {is_list_true}")
    return is_list_true


def parse_homework_status(homework: Dict) -> str:
    """Takes a response from api homework and parse answers for user."""
    homework_name = homework.get("homework_name")
    statuses = {
        "rejected": "К сожалению в работе нашлись ошибки.",
        "reviewed": "Проект взят в работу ревьювером.",
        "approved": "Ревьюеру всё понравилось, можно приступать к следующему уроку.",
    }

    return f'У вас проверили работу "{homework_name}"!\n\n{statuses[homework.get("status")]}'


def get_homework_statuses(current_timestamp: int) -> dict:
    """Return student homework status from yandex api in JSON format."""
    data = {"from_date": current_timestamp}
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    homework_statuses = requests.get(
        PRAKTIKUM_API_URL,
        params=data,
        headers=headers,
    )
    return homework_statuses.json()


try:
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
except telegram.error.TelegramError as e:
    logger.error(f"Bot was not created. Error: {e}")


def send_message(message: str, bot_client=bot):
    "Sends message to student telegram about homework status."
    try:
        return bot_client.send_message(chat_id=CHAT_ID, text=message)
    except:
        raise


def main():
    logger.debug("Bot is starting...")

    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if check_api_for_mandatory(new_homework):
                try:
                    homework = new_homework.get("homeworks")[0]
                    text_for_message = parse_homework_status(homework)
                    send_message(text_for_message)
                    logger.info("Message was send")
                except:
                    logger.error(f"Error while trying send message: {e}")
                    raise
            current_timestamp = new_homework.get(
                "current_date", current_timestamp
            )  # обновить timestamp
            time.sleep(CHECKING_TIME)

        except Exception as e:
            error = logger.exception(f"Бот столкнулся с ошибкой: {e}")
            send_message(error)
            time.sleep(5)


if __name__ == "__main__":
    main()
