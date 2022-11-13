from telebot.async_telebot import AsyncTeleBot
import asyncio
from bs4 import BeautifulSoup
from telebot import types
import numpy as np
import logging
import pickle
import requests

# Logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

handler = logging.FileHandler('telebot.log')
handler.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)


# Collecting information about the drug

class CollectData:

    def __init__(self, med):
        self.med = med
        self.info = ''

    def get_features(self):
        features = [self.fda(self.med), self.pubmed(self.med), self.ema(self.med),
                    self.drugs(self.med), self.who(self.med), self.rxlist(self.med)]
        features = np.array(features).reshape(1, -1)
        return features

    def fda(self, med):
        try:
            med = med.upper()
            letter = med[0]
            url = 'https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=browseByLetter.page&productLetter=' \
                  + letter + '&ai=0'
            response = requests.get(url, timeout=20)
            bs = BeautifulSoup(response.text, "lxml")
            drugs = bs.find_all(title='Click to expand drug name')
            for drug in drugs:
                if ' ' + med + ' ' in ' ' + drug.text + ' ':
                    self.info += f'FDA ✅: {url}\n'
                    return 1
            self.info += f'FDA 🚫\n'
            return 0
        except Exception:
            logger.exception(f'Error occurred while scraping fda.com with {med}')
            return None

    def pubmed(self, med):
        try:
            med = med.replace(' ', '+')
            url = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + med + \
                  '%5Btitle%5D&filter=pubt.clinicaltrial&filter=pubt.meta-analysis'
            response = requests.get(url, timeout=10)
            bs = BeautifulSoup(response.text, "lxml")
            if bs.find('span', class_='no-results-query') or \
                    bs.find('em', class_='altered-search-explanation query-error-message'):
                self.info += f'PubMed 🚫\n'
                return 0
            elif bs.find('span', class_='value'):
                results = bs.find('span', class_='value').text.replace(',', '')
                self.info += f'PubMed - {results} ✅: {url}\n'
                return results
            elif bs.find('span', class_='single-result-redirect-message'):
                self.info += f'PubMed - {1} ✅: {url}\n'
                return 1
            else:
                self.info += f'PubMed 🚫\n'
                return 0
        except Exception:
            logger.exception(f'Error occurred while scraping pubmed with {med}')
            return None

    def ema(self, med):
        try:
            med_url = med.replace(' ', '%20').lower()
            url = 'https://www.ema.europa.eu/en/medicines/field_ema_web_categories%253Aname' \
                  '_field/Human/search_api_aggregation_ema_active_substance_and_inn_common_name/' + med_url
            response = requests.get(url, timeout=10)
            bs = BeautifulSoup(response.text, "lxml")
            result = int(bool(bs.find('ul', class_='ema-listings view-content-solr ecl-u-pt-m')))
            if result:
                self.info += f'EMA ✅: {url}\n'
            else:
                self.info += f'EMA 🚫\n'
            return result
        except Exception:
            logger.exception(f'Error occurred while scraping ema.com with {med}')
            return None

    def drugs(self, med):
        try:
            two_letters = med.lower()[:2]
            url = 'https://www.drugs.com/alpha/' + two_letters + '.html'
            response = requests.get(url, timeout=10)
            bs = BeautifulSoup(response.text, "lxml")
            if bs.find('h1', text='Page Not Found'):
                return 0
            else:
                table = bs.find('div', class_='contentBox')
                drugs = table.find_all('a')
                for drug in drugs:
                    if ' ' + med.lower() + ' ' in ' ' + drug.text.lower() + ' ':
                        self.info += f'drugs ✅: {url}\n'
                        return 1
                self.info += f'drugs 🚫\n'
                return 0
        except Exception:
            logger.exception(f'Error occurred while scraping drugs.com with {med}')
            return None

    def who(self, med):
        try:
            med_url = med.replace(' ', '%20')
            url = 'https://list.essentialmeds.org/?query=' + med_url
            response = requests.get(url, timeout=10)
            bs = BeautifulSoup(response.text, "lxml")
            if bs.find('h5', class_='medicine-name'):
                table = bs.find('div', class_='medicines-list-container')
                drugs = table.find_all('span')
                for name in drugs:
                    if ' ' + med.lower() + ' ' in ' ' + name.text.lower() + ' ':
                        self.info += f'WHO ✅: {url}\n'
                        return 1
            self.info += f'WHO 🚫\n'
            return 0
        except Exception:
            logger.exception(f'Error occurred while scraping who.com with {med}')
            return None

    def rxlist(self, med):
        try:
            letter = med[0].lower()
            url = 'https://www.rxlist.com/drugs/alpha_' + letter + '.htm'
            response = requests.get(url, timeout=10)
            bs = BeautifulSoup(response.text, "lxml")
            if bs.find('div', class_='AZ_results'):
                table = bs.find('div', class_='AZ_results')
                drugs = table.find_all('a')
                for drug in drugs:
                    if ' ' + med.lower() + ' ' in ' ' + drug.text.lower() + ' ':
                        self.info += f'RxList ✅: {url}\n'
                        return 1
            self.info += f'RxList 🚫\n'
            return 0
        except Exception:
            logger.exception(f'Error occurred while scraping rxlist.com with {med}')
            return None


# Checking results, scaling the data and making prediction

scaler = pickle.load(open('scaler.sav', 'rb'))
ml_model = pickle.load(open('finalized_model.sav', 'rb'))


def some_trouble_with(med):
    is_short_name = len(med) <= 1
    isdigit = med.replace(' ', '').isdigit()
    not_ascii = not med.isascii()
    if is_short_name or isdigit or not_ascii:
        return True
    return False


def nans_in_features(med, features):
    if None in features:
        logger.warning(f'Some NaNs in the drug features, look at that: {med}, {features}')
        return True
    return False


def scale(data):
    return scaler.transform(data)


def make_prediction(data):
    probability = ml_model.predict_proba(data)[0][1]
    return probability


# His majesty telegram bot

with open('token.txt', 'r') as file:
    TOKEN = file.read()

bot = AsyncTeleBot(TOKEN)

START_MESSAGE = "Hello! 😊 This is a bot for checking the reliability of medicines. \
Overall evaluation of the drug based on analysis of its presence in such sources as FDA, \
European Medicines Agency, PubMed, Drugs. com, RxList and WHO.\n \
Keep in mind that reliability does not mean that a drug is safe, has no side effects, or \
prescribed correctly. This means that it is likely to have a positive effect on the \
conditions described in the instructions. Meanwhile, unreliable drugs are most likely to have no effect at all.\n \
To get this information enter the international nonproprietary name (INN) or active pharmaceutical \
ingredient of the drug in English."

HELP_MESSAGE = 'Enter the international nonproprietary name (INN) or active pharmaceutical \
ingredient of the drug in English to get an overall rating of its reliability.'

ERROR_MESSAGE = 'Something went wrong. Try again and make sure that you enter the drug name correctly.'
RELIABLE_MESSAGE = ' is a reliable drug 👍. For more details check the following resources:\n'
UNRELIABLE_MESSAGE = ' is not a reliable drug 👎. For more details check the following resources:\n'
CHECK_MANUAL_MESSAGE = ' is a questionable drug. I would recommend you check it manually. For that ' \
                       'check the following resources:\n'


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
            probability = make_prediction(scale(drug_features))
            if probability > 0.55:
                await bot.send_message(message.chat.id, med.capitalize() + RELIABLE_MESSAGE + drug.info)
            elif probability < 0.35:
                await bot.send_message(message.chat.id, med.capitalize() + UNRELIABLE_MESSAGE + drug.info)
            else:
                await bot.send_message(message.chat.id, med.capitalize() + CHECK_MANUAL_MESSAGE + drug.info)


asyncio.run(bot.polling())

