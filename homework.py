import logging
import logging.config
import os
import time
from typing import Dict

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.config.fileConfig("logging.ini")
logger = logging.getLogger()


def parse_homework_status(homework: Dict) -> str:
    """Takes a response from api homework and parse answers for user."""
    homework_name = homework.get("homework_name")
    if homework.get("status") == "rejected":
        verdict = "К сожалению в работе нашлись ошибки."
    else:
        verdict = (
            "Ревьюеру всё понравилось, можно приступать к следующему уроку."
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp: int) -> dict:
    """Return student homework status from yandex api in JSON format."""
    data = {"from_date": current_timestamp}
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    homework_statuses = requests.get(
        "https://praktikum.yandex.ru/api/user_api/homework_statuses/",
        params=data,
        headers=headers,
    )
    return homework_statuses.json()


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def send_message(message: str, bot_client=bot):
    "Sends message to student telegram about homework status."
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    logger.debug("Bot is starting...")

    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get("homeworks"):
                send_message(
                    parse_homework_status(new_homework.get("homeworks")[0])
                )
                logger.info("Message was send")
            current_timestamp = new_homework.get(
                "current_date", current_timestamp
            )  # обновить timestamp
            time.sleep(300)

        except Exception as e:
            error = logger.error(f"Бот столкнулся с ошибкой: {e}")
            send_message(error)
            time.sleep(5)


if __name__ == "__main__":
    main()
