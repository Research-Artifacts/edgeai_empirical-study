import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

last_year_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

NUM_COMMITS = 50
NUM_STARS = 2

PER_PAGE = int(os.getenv('PER_PAGE'))
MAX_RESP = int(os.getenv('MAX_RESP'))

USERNAME = os.getenv('GITHUB_USERNAME')
TOKEN    = os.getenv('API_TOKEN')

headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}
