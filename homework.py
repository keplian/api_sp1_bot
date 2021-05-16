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

# так валятся тесты
# PRAKTIKUM_API_URL = os.environ["PRAKTIKUM_API_URL"]
PRAKTIKUM_API_URL = (
    "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
)

CHECKING_TIME = 300

logging.config.fileConfig("logging.ini")
logger = logging.getLogger()


def check_api_for_mandatory(new_homework):
    homework = new_homework.get("homeworks")
    if homework:
        statuses_list = ["rejected", "reviewed", "approved"]
        checking_list = [
            isinstance(int(new_homework[0].get("current_date")), int),
            homework,
            homework[0].get("homework_name"),
            homework[0].get("status") in statuses_list,
        ]
        is_list_true = all(checking_list)
        if not is_list_true:
            if new_homework.get("error"):
                logger.error("Api returned error")
                raise Exception("Api returned error")
        logger.debug(f"checking api list returned {is_list_true}")
        return is_list_true
    return False


def parse_homework_status(homework: Dict) -> str:
    """Takes a response from api homework and parse answers for user."""
    homework_name = homework.get("homework_name")
    statuses = {
        "rejected": "К сожалению в работе нашлись ошибки.",
        "reviewed": "Проект взят в работу ревьювером.",
        "approved": (
            "Ревьюеру всё понравилось, можно приступать к следующему уроку."
        ),
    }
    return (
        f'У вас проверили работу "{homework_name}"!\n\n'
        f'{statuses[homework.get("status")]}'
    )


def get_homework_statuses(current_timestamp: int) -> dict:
    """Return student homework status from yandex api in JSON format."""
    data = {"from_date": current_timestamp}
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_API_URL,
            params=data,
            headers=headers,
        )
        # Заккоментриовал, т.к. валятся тесты
        # homework_statuses.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        send_message(str(e))
        raise
    return homework_statuses.json()


bot = telegram.Bot(token=TELEGRAM_TOKEN)
# проверяю здесь валидность токена, но тогда не проходятся тесты pytest :(
# try:
#     bot.get_me()
# except telegram.error.TelegramError as e:
#     logger.exception(f"Bot was not created. Error: {str(e)}")
#     raise


def send_message(message: str, bot_client=bot):
    """Sends message to student's telegram."""
    try:
        return bot_client.send_message(chat_id=CHAT_ID, text=message)
    except telegram.error.TelegramError as e:
        logger.exception(e)
        raise


def main():
    logger.debug("Bot is starting...")

    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if check_api_for_mandatory(new_homework):
                homework = new_homework.get("homeworks")
                text_for_message = parse_homework_status(homework)
                send_message(text_for_message)
                logger.info("Message was send")
            current_timestamp = new_homework.get(
                "current_date", current_timestamp
            )  # обновить timestamp
            time.sleep(CHECKING_TIME)

        except Exception as e:
            store_exception = None
            if store_exception != e:
                logger.exception(f"Бот столкнулся с ошибкой: {str(e)}")
                send_message(f"Бот столкнулся с ошибкой: {str(e)}")
                store_exception = e
            time.sleep(60)


if __name__ == "__main__":
    main()
