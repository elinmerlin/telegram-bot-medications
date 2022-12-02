TABLE = {'Med': [],
         'FDA': [],
         'PubMed': [],
         'EMA': [],
         'drugs.com': [],
         'WHO': [],
         'RxList': [],
         'Target': []
        }

FDA_URL = 'https://www.accessdata.fda.gov/scripts/cder/daf/index.' \
          'cfm?event=browseByLetter.page&productLetter=first_letter&ai=0'
PUBMED_URL = 'https://pubmed.ncbi.nlm.nih.gov/?term=med_name%5Btitle' \
             '%5D&filter=pubt.clinicaltrial&filter=pubt.meta-analysis'
EMA_URL = 'https://www.ema.europa.eu/en/medicines/field_ema_web_categor' \
          'ies%253Aname_field/Human/search_api_aggregation_ema_active_' \
          'substance_and_inn_common_name/'
DRUGS_URL = 'https://www.drugs.com/alpha/two_letters.html'
WHO_URL = 'https://list.essentialmeds.org/?query='
RXLIST_URL = 'https://www.rxlist.com/drugs/alpha_first_letter.htm'

START_MESSAGE = "Hello! 😊 This is a bot for checking the reliability of medicines. \
Overall evaluation of the drug based on the analysis of its presence in such sources as FDA, \
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


UPPER_THRESHOLD = 0.55
LOWER_THRESHOLD = 0.35
