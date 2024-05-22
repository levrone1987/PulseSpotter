import os

from dotenv import load_dotenv

from config import ROOT_DIR


load_dotenv(ROOT_DIR.joinpath(".env"))

SPIDER_CONFIG = {
    'handelsblatt_crawler': {
        'max_pages': 1,
        'start_urls': [
            'https://www.handelsblatt.com/finanzen/banken-versicherungen/',
            'https://www.handelsblatt.com/finanzen/banken-versicherungen/banken/',
            'https://www.handelsblatt.com/finanzen/banken-versicherungen/versicherer/',
            'https://www.handelsblatt.com/finanzen/maerkte/',
            'https://www.handelsblatt.com/finanzen/maerkte/marktberichte/',
            'https://www.handelsblatt.com/finanzen/maerkte/aktien/',
            'https://www.handelsblatt.com/finanzen/maerkte/devisen-rohstoffe/',
            'https://www.handelsblatt.com/finanzen/maerkte/anleihen/',
            'https://www.handelsblatt.com/finanzen/maerkte/boerse-inside/',
            'https://www.handelsblatt.com/finanzen/anlagestrategie/',
            'https://www.handelsblatt.com/finanzen/anlagestrategie/trends/',
            'https://www.handelsblatt.com/finanzen/anlagestrategie/fonds-etf/',
            'https://www.handelsblatt.com/finanzen/anlagestrategie/zertifikate/',
            'https://www.handelsblatt.com/finanzen/anlagestrategie/musterdepots/',
            'https://www.handelsblatt.com/finanzen/immobilien/',
            'https://www.handelsblatt.com/finanzen/vorsorge/',
            'https://www.handelsblatt.com/finanzen/vorsorge/altersvorsorge-sparen/',
            'https://www.handelsblatt.com/finanzen/vorsorge/versicherung/',
            'https://www.handelsblatt.com/finanzen/steuern-recht/',
            'https://www.handelsblatt.com/finanzen/steuern-recht/steuern/',
            'https://www.handelsblatt.com/finanzen/steuern-recht/recht/',
            'https://www.handelsblatt.com/finanzen/geldpolitik/',
        ],
    }
}

# MongoDB configuration
MONGO_URI = 'mongodb+srv://{username}:{password}@cluster-v1.gihuvyk.mongodb.net/'.format(
    username=os.getenv('MONGO_USER'),
    password=os.getenv('MONGO_PASSWORD')
)
MONGO_DATABASE = 'insightfinder-dev'
MONGO_COLLECTION = 'content'

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
