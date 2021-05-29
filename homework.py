import logging
import os
import time

import requests
import telegram
import tg_logger
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
tg_logger.setup(logger, token=TELEGRAM_TOKEN, users=[CHAT_ID])


def parse_homework_status(homework):
    homework_name = homework["homework_name"]
    try:
        if homework["status"] == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        else:
            verdict = ('Ревьюеру всё понравилось, можно '
                       'приступать к следующему уроку.')
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except Exception as error:
        logging.error(error, exc_info=True)


def get_homework_statuses(current_timestamp):
    try:
        params = {'from_date': current_timestamp}
        homework_statuses = requests.get(
            'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
            params=params)
        return homework_statuses.json()
    except Exception as error:
        logger.error(error, exc_info=True)


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client)
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)
            time.sleep(300)

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
