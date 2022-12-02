import logging
import pickle

from bs4 import BeautifulSoup
import numpy as np
import numpy.typing as npt
import requests

from constants import *

# Logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

handler = logging.FileHandler('./logs/telebot.log')
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
            url = FDA_URL.replace('first_letter', letter)
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
            url = PUBMED_URL.replace('med_name', med)
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
            med_name = med.replace(' ', '%20').lower()
            url = EMA_URL + med_name
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
            url = DRUGS_URL.replace('two_letters', two_letters)
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
            med_name = med.replace(' ', '%20')
            url = WHO_URL + med_name
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
            first_letter = med[0].lower()
            url = RXLIST_URL.replace('first_letter', first_letter)
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

scaler = pickle.load(open('./app/scaler.sav', 'rb'))
ml_model = pickle.load(open('./app/finalized_model.sav', 'rb'))


def some_trouble_with(med: str) -> bool:
    """ Checks if the given drug name is valid """

    is_short_name = len(med) <= 1
    isdigit = med.replace(' ', '').isdigit()
    not_ascii = not med.isascii()
    if is_short_name or isdigit or not_ascii:
        return True
    return False


def nans_in_features(med: str, features: npt.NDArray) -> bool:
    """ Checks if NaNs in the list of the features """

    if None in features:
        logger.warning(f'Some NaNs in the drug features, look at that: {med}, {features}')
        return True
    return False


def scale(data: npt.NDArray) -> npt.NDArray:
    """ Scales the data """

    return scaler.transform(data)


def make_prediction(data: npt.NDArray) -> float:
    """ Makes prediction """

    probability = ml_model.predict_proba(data)[0][1]
    return probability
