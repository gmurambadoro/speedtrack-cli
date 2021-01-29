import json
import os
import subprocess
import sys
from os.path import dirname

import pytz
from dateutil.parser import *
from tzlocal import get_localzone
from pymongo import MongoClient

from dotenv import load_dotenv

if not load_dotenv(dotenv_path='./.env'):
    print('E: Cannot find environment file .env in ' + dirname(__file__))
    sys.exit(1)

MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_PORT = int(os.getenv('MONGO_PORT') or '27017')
MONGO_DATABASE = os.getenv('MONGO_DATABASE')


def utc_to_locale_timestamp(timestamp) -> str:
    tz_locale = get_localzone()
    date_utc = parse(timestamp)
    date_locale = date_utc.replace(tzinfo=pytz.utc).astimezone(tz_locale)
    return date_locale.strftime('%Y-%m-%dT%H:%M:%S%z')


try:
    print('Running speedtest command. Please wait...')
    result = subprocess.run(['speedtest', '--json'], stdout=subprocess.PIPE)

    print('Analysing result...')

    doc = json.loads(result.stdout)

    if not doc['download']:
        raise RuntimeError('An error was encountered when downloading: ' + str(result.stdout))

    # preserve the timestamp as obtained from server
    doc['timestamp_utc'] = doc['timestamp']

    # convert timestamp field to locale date object
    doc['timestamp'] = utc_to_locale_timestamp(doc['timestamp'])

    client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)

    database = client.get_database(MONGO_DATABASE)

    collection = database.get_collection('speeds')

    print('Saving the result to database...')

    collection.insert_one(document=doc)

    print()

    print(doc)

    print()

    print('[OK] Command successfully completed.')

    sys.exit(0)
except FileNotFoundError as err:
    print('E: ' + str(err))
except RuntimeError as err:
    print('E: ' + str(err))

sys.exit(1)
