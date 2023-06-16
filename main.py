import os
import textwrap as tw
from argparse import ArgumentParser
from dotenv import load_dotenv
import requests
import telebot


def main():
    """
    Parsing chat_id argument.
    """
    arg_parser = ArgumentParser(
        description='Бот для уведомлений о проверке заданий на dvmn.org'
    )
    arg_parser.add_argument(
        'id',
        help="ID чата, в который будут отправляться уведомления."
    )
    args = arg_parser.parse_args()
    CHAT_ID = args.id

    #  Reading tokens from .env
    load_dotenv()
    API_TOKEN = os.getenv("BOT_TOKEN")

    #  Launching the bot.
    bot = telebot.TeleBot(API_TOKEN)

    #  Request URL and parameters setup.
    dvmn_lpoll_url = "https://dvmn.org/api/long_polling/"
    auth_token_header = {
        "Authorization": os.getenv("DVMN_TOKEN")
    }
    timestamp_param = {}

    #  Commence polling.
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
        dvmn_lpoll_response.raise_for_status()

        dvmn_response_structured = dvmn_lpoll_response.json()
        if dvmn_response_structured["status"] == "timeout":
            timestamp_param['timestamp'] = dvmn_response_structured["timestamp_to_request"]
        elif dvmn_response_structured["status"] == "found":
            try:
                send_notification(bot, CHAT_ID, dvmn_response_structured)
            except Exception as e:
                print(f'Error sending notification: {e}')
            timestamp_param['timestamp'] = dvmn_response_structured["last_attempt_timestamp"]


def send_notification(bot: telebot.TeleBot, chat_id: int, response_json: dict):
    """
    Sends a notification to the specified chat ID
    with information about a new attempt on a lesson.

    """

    attempt = response_json['new_attempts'][0]
    notification_text = f"""
        У Вас проверили работу «{attempt['lesson_title']}\n
        {'К сожалению, в работе нашлись ошибки.' if attempt['is_negative'] else
        'Преподавателю всё понравилось, можно приступать к следующему уроку!'}

        Ссылка на урок: {attempt['lesson_url']}
    """

    bot.send_message(
        chat_id,
        tw.dedent(notification_text),
        disable_web_page_preview=True)


if __name__ == "__main__":
    main()
