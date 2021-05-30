import json
import logging
import os
import time

import requests
import telegram
import tg_logger
from dotenv import load_dotenv

load_dotenv()

URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
tg_logger.setup(logger, token=TELEGRAM_TOKEN, users=[CHAT_ID])


def parse_homework_status(homework):
    status = {
        'rejected': 'К сожалению в работе нашлись ошибки.',
        'approved': ('Ревьюеру всё понравилось, можно '
                     'приступать к следующему уроку.')
    }
    try:
        homework_name = homework["homework_name"]
        if homework["status"] == 'reviewing':
            return (f'Работа "{homework_name}" взята в ревью')
        return (f'У вас проверили работу "{homework_name}"!\n\n'
                f'{status[homework["status"]]}')
    except KeyError as error:
        logger.error(f'Ключ {error} не найден', exc_info=True)
        raise


def get_homework_statuses(current_timestamp):
    try:
        params = {'from_date': current_timestamp}
        homework_statuses = requests.get(
            URL,
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
            params=params)
        return homework_statuses.json()
    except json.JSONDecodeError:
        logger.error("Ответ не соотвествует формату json", exc_info=True)
        raise
    except requests.RequestException:
        logger.error("При обработке запроса возникла ошибка", exc_info=True)
        raise


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
                logging.info("Message send")
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)
        except Exception as e:
            logger.error(f'Бот столкнулся с ошибкой: {e}')
        finally:
            time.sleep(300)


if __name__ == '__main__':
    main()
