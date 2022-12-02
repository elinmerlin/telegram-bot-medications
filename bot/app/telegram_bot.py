import os
import warnings

from telebot.async_telebot import AsyncTeleBot
from telebot import types
import asyncio

from collect_and_check_the_data import *

warnings.filterwarnings("ignore")

bot = AsyncTeleBot(os.getenv('TOKEN'))


@bot.message_handler(commands=['start', 'help'])
async def start(message):
    start_buttons = ['/start', '/help']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    if message.text == '/start':
        await bot.send_message(message.chat.id, START_MESSAGE, reply_markup=keyboard)
    else:
        await bot.send_message(message.chat.id, HELP_MESSAGE, reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
async def handle_text(message):
    med = message.text.lower().strip()
    if some_trouble_with(med):
        await bot.send_message(message.chat.id, ERROR_MESSAGE)
    else:
        drug = CollectData(med)
        drug_features = drug.get_features()
        if nans_in_features(med, drug_features):
            await bot.send_message(message.chat.id, ERROR_MESSAGE)
        else:
            scaled_features = scale(drug_features)
            probability = make_prediction(scaled_features)
            if probability > UPPER_THRESHOLD:
                await bot.send_message(message.chat.id, med.capitalize() + RELIABLE_MESSAGE + drug.info)
            elif probability < LOWER_THRESHOLD:
                await bot.send_message(message.chat.id, med.capitalize() + UNRELIABLE_MESSAGE + drug.info)
            else:
                await bot.send_message(message.chat.id, med.capitalize() + CHECK_MANUAL_MESSAGE + drug.info)


asyncio.run(bot.polling())
