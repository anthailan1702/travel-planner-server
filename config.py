import os

from dotenv import load_dotenv

base_dir = os.getcwd()
dotenv_path = base_dir + '/.env'
load_dotenv(dotenv_path=dotenv_path)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'
    GOOGLE_PLACE_API_KEY = os.environ.get('GOOGLE_PLACE_API_KEY')
    FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
    FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')
