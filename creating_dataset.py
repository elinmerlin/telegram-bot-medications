from bs4 import BeautifulSoup
from copy import deepcopy
import logging
import pandas as pd
import requests
import re
import lxml

# Creating logger

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('errors_warnings.log')
handler.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)

# Creating a class for scraping websites and collecting the necessary information for our future dataset

class CollectData:

    def __init__(self, table, meds, target):
        self.meds = meds
        self.target = target
        self.table = deepcopy(table)

    def get_table(self):
        for med in self.meds:
            self.table['Med'].append(med)
            self.table['FDA'].append(self.fda(med))
            self.table['PubMed'].append(self.pubmed(med))
            self.table['EMA'].append(self.ema(med))
            self.table['drugs.com'].append(self.drugs(med))
            self.table['WHO'].append(self.who(med))
            self.table['RxList'].append(self.rxlist(med))
            self.table['Target'].append(self.target)
        return self.table

    def fda(self, med):
        try:
            med = med.upper()
            letter = med[0]
            url = 'https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=browseByLetter.page&productLetter=' + letter + '&ai=0'
            response = requests.get(url, timeout=20)
            bs = BeautifulSoup(response.text, "lxml")
            drugs = bs.find_all(title='Click to expand drug name')
            for drug in drugs:
                if ' ' + med + ' ' in ' ' + drug.text + ' ':
                    return 1
            return 0
        except:
            logger.exception(f'Error occured while scraping fda.com with {med}')
            return None

    def pubmed(self, med):
        try:
            med = med.replace(' ', '+')
            url = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + med + '%5Btitle%5D&filter=pubt.clinicaltrial&filter=pubt.meta-analysis'
            response = requests.get(url, timeout=10)
            bs = BeautifulSoup(response.text, "lxml")
            if bs.find('span', class_='no-results-query') or bs.find('em',
                                                                     class_='altered-search-explanation query-error-message'):
                return 0
            elif bs.find('span', class_='value'):
                results = bs.find('span', class_='value').text.replace(',', '')
                return results
            elif bs.find('span', class_='single-result-redirect-message'):
                return 1
            else:
                return 0
        except:
            logger.exception(f'Error occured while scraping pubmed.com with {med}')
            return None

    def ema(self, med):
        try:
            med_url = med.replace(' ', '%20').lower()
            url = 'https://www.ema.europa.eu/en/medicines/field_ema_web_categories%253Aname_field/Human/search_api_aggregation_ema_active_substance_and_inn_common_name/' + med_url
            response = requests.get(url, timeout=10)
            bs = BeautifulSoup(response.text, "lxml")
            return int(bool(bs.find('ul', class_='ema-listings view-content-solr ecl-u-pt-m')))
        except:
            logger.exception(f'Error occured while scraping ema.com with {med}')
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
                        return 1
                return 0
        except:
            logger.exception(f'Error occured while scraping drugs.com with {med}')
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
                        return 1
            return 0
        except:
            logger.exception(f'Error occured while scraping WHO with {med}')
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
                        return 1
            return 0
        except:
            logger.exception(f'Error occured while scraping RxList with {med}')
            return None


TABLE = {'Med': [],
         'FDA': [],
         'PubMed': [],
         'EMA': [],
         'drugs.com': [],
         'WHO': [],
         'RxList': [],
         'Target': []
        }

# I got prepared lists of potentially reliable and unreliable medications.
# I am going to load them and pass into the CollectData class.

with open('data/reliable_meds.txt', 'r') as file:
    reliable_meds = file.readlines()
reliable_meds = [med.strip() for med in reliable_meds]

with open('data/unreliable_meds.txt', 'r') as file:
    unreliable_meds = file.readlines()
unreliable_meds = [med.strip() for med in unreliable_meds]

reliable = CollectData(TABLE, reliable_meds, target=1)
reliable_meds_info = reliable.get_table()
unreliable = CollectData(TABLE, unreliable_meds, target=0)
unreliable_meds_info = unreliable.get_table()

# The resulting dataset will consist of both classes

reliable_meds_info = pd.DataFrame(reliable_meds_info)
unreliable_meds_info = pd.DataFrame(unreliable_meds_info)
all_medications = pd.concat([reliable_meds_info, unreliable_meds_info])

# all_medications.to_csv('data/medications.csv', sep=',')