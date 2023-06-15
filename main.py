import os
from argparse import ArgumentParser
from dotenv import load_dotenv
import requests
import telebot

"""
Parsing chat_id argument.
"""
arg_parser = ArgumentParser(description='Бот для отправки уведомлений о проверке заданий на сайте dvmn.org')
arg_parser.add_argument('id', help="ID чата, в который будут отправляться уведомления.")
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
params = {}


def send_notification(response_json):
    """
    Sends a notification to the specified chat ID with information about a new attempt on a lesson.

    """

    attempt = response_json['new_attempts'][0]
    notification_text = f"""
У Вас проверили работу «{attempt['lesson_title']}»
    
{'К сожалению, в работе нашлись ошибки.' if attempt['is_negative']
    else 'Преподавателю всё понравилось, можно приступать к следующему уроку!'}
    
Ссылка на урок: {attempt['lesson_url']}
    """
    try:
        bot.send_message(CHAT_ID, notification_text, disable_web_page_preview=True)
    except Exception as e:
        print(f'Error sending notification: {e}')


if __name__ == "__main__":
    while True:
        try:
            dvmn_response = requests.get(dvmn_lpoll_url, headers=auth_token_header, params=params)
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            continue

        if dvmn_response.json()["status"] == "timeout":
            params['timestamp'] = dvmn_response.json()["timestamp_to_request"]
        elif dvmn_response.json()["status"] == "found":
            send_notification(dvmn_response.json())
            params['timestamp'] = dvmn_response.json()["last_attempt_timestamp"]
