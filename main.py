from environs import Env
import textwrap as tw
from argparse import ArgumentParser
import requests
import telebot
import logging

logger = logging.getLogger('TeleBot')


class TGLogsHandler(logging.Handler):
    def __init__(self, bot_token: str, chat_id: int or str):
        super().__init__()
        self.bot = telebot.TeleBot(bot_token)
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        msg = self.bot.send_message(self.chat_id, log_entry)


def main():
    env = Env()
    env.read_env()
    api_token = env.str("BOT_TOKEN")
    admin_id = env.int("ADMIN_CHAT_ID")

    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    logger.info('Commence logging.')
    logger.addHandler(TGLogsHandler(api_token, admin_id))

    arg_parser = ArgumentParser(
        description='Бот для уведомлений о проверке заданий на dvmn.org'
    )
    arg_parser.add_argument(
        '--id',
        help="ID чата, в который будут отправляться уведомления. This function is deprecated. Use env vars instead.",
        type=int
    )
    args = arg_parser.parse_args()
    if args.id:
        chat_id = args.id
    else:
        chat_id = env.int('USER_ID')

    bot = telebot.TeleBot(api_token)
    logger.info(f'Bot is launched. Chat id is {chat_id}.')

    dvmn_lpoll_url = "https://dvmn.org/api/long_polling/"
    auth_token_header = {
        "Authorization": env.str("DVMN_TOKEN")
    }
    timestamp_param = {}

    while True:
        try:
            dvmn_lpoll_response = requests.get(
                dvmn_lpoll_url,
                headers=auth_token_header,
                params=timestamp_param
            )
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        try:
            dvmn_lpoll_response.raise_for_status()
        except requests.HTTPError as err:
            logger.error('Бот упал с ошибкой')
            logger.exception(err)

        reviews = dvmn_lpoll_response.json()
        if reviews["status"] == "timeout":
            timestamp_param['timestamp'] = reviews["timestamp_to_request"]
        elif reviews["status"] == "found":
            try:
                send_notification(bot, chat_id, reviews)
            except requests.HTTPError or requests.ConnectionError as err:
                logger.error(f'Error sending notification: {err}')
                logger.exception(err)
            timestamp_param['timestamp'] = reviews["last_attempt_timestamp"]


def send_notification(bot: telebot.TeleBot, chat_id: int, reviews: dict):
    """Send notification

    Sends a notification to the specified chat ID
    with information about a new attempt on a lesson.

    Args:
        bot (TeleBot): A bot object used to send message
        chat_id (int): ID of a chat to where send the notification
        reviews (dict): Json-format reviews from Devman API response

    Returns:
        Message: Message object of message that has been sent

    """
    attempt = reviews['new_attempts'][0]
    notification_text = f"""
        У Вас проверили работу «{attempt['lesson_title']}\n
        {'К сожалению, в работе нашлись ошибки.' if attempt['is_negative'] else
        'Преподавателю всё понравилось, можно приступать к следующему уроку!'}

        Ссылка на урок: {attempt['lesson_url']}
    """
    msg = bot.send_message(
        chat_id,
        tw.dedent(notification_text),
        disable_web_page_preview=True)

    return msg


if __name__ == "__main__":
    main()
