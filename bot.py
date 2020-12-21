#!/usr/bin/env python3

import logging

import telebot
import yaml

from exchange import Exchange

LOG = logging.getLogger('Bot')
USAGE_HELP = """<имя валюты цену которой хотите узнать> <имя валюты в которой надо узнать цену первой валюты> <количество первой валюты> /values стоимость всех доступных валют"""

with open('config-bot.yml', 'r') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

loglevel = config['loglevel'].upper()
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    level=loglevel)
bot = telebot.TeleBot(config['token'])
exchange = Exchange()


@bot.message_handler(commands=['start', 'help', 'h'])
def print_help(message: telebot.types.Message):
    bot.send_message(message.chat.id, USAGE_HELP)


@bot.message_handler(commands=['values'])
def get_all_rates(message: telebot.types.Message):
    try:
        data, base = exchange.get_all_rates()
    except Exception as e:
        LOG.critical(f"Can't get exchange values. Error: {repr(e)}")
        return
    bot.send_message(message.chat.id, '\n'.join(data) + f'\nBase: {base}')


@bot.message_handler(content_types=['text'])
def parse_cur(message: telebot.types.Message):
    try:
        text = exchange.get_course_from_text(message.text)
    except Exception as e:
        LOG.exception(f"Can't get course from API")
        text = repr(e)
    bot.reply_to(message, text)


if __name__ == '__main__':
    bot.polling()
