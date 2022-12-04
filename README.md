# telegram-bot-medications
<<<<<<< HEAD
=======

Hello! 😊 This is a bot for checking the reliability of medicines. Overall evaluation of the drug is based on the analysis of its presence in the following  sources:
- [Food and Drug Administration](https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm), 
- [European Medicines Agency](https://www.ema.europa.eu/en/medicines/field_ema_web_categories%253Aname_field/Human/search_api_aggregation_ema_active_substance_and_inn_common_name/idebenone), 
- [PubMed](https://pubmed.ncbi.nlm.nih.gov), 
- [Drugs](https://www.drugs.com/drug_information.html), 
- [RxList](https://www.rxlist.com/drugs/alpha_a.htm), 
- [World Health Organization](https://list.essentialmeds.org/?query=). 

Keep in mind that reliability does not mean that the drug is safe, has no side effects, or prescribed correctly. This means that it is likely to have a positive effect on the conditions described in the instructions. Meanwhile, unreliable drugs are most likely to have no effect at all. To get this information the user should enter the international nonproprietary name (INN) or active pharmaceutical ingredient of the drug in English. 
The user will also be provided with the original sources to check the information themselves.

Here are some examples of it:

<img width="613" alt="Screenshot 2022-12-04 at 14 00 39" src="https://user-images.githubusercontent.com/96263809/205487674-12e16bc8-373d-4955-8905-3e537b01bd1b.png">


<img width="617" alt="Screenshot 2022-12-04 at 14 01 20" src="https://user-images.githubusercontent.com/96263809/205487679-8cd7705f-a669-4317-9115-6cb8cb2c990c.png">




The algorithm evaluating drug reliability includes the following steps:

>- Scraping the given websites collecting information about the drug;
>- Collected information is analysed by the logistic regression machine learning model that returns probability of the drug being reliable;
>- The drug is evaluated as reliable if the probability is over 0.55 and unreliable if it is less than 0.35;
>- If the probability is between 0.35 and 0.55 the bot suggests the user to check the sources themselves (which is OK only for healthcare workers).

The logistic regression model is fitted to the data that has been collected by me earlier. How it's done you can find in the /bot/data/collecting_data.py.


To launch your own telegram-bot based on the same algorithm you need to store your bot token in .env file in the root directory.
Then to deploy it from the root folder:

    docker-compose up -d --build
    
To switch containers off:

    docker-compose down -v
>>>>>>> 06e8831e246d423c29e333fab033b100680c4e28
