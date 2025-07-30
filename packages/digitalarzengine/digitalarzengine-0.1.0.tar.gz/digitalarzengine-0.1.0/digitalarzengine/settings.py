import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
PAK_DATA_DIR= os.path.join(MEDIA_DIR, 'pak')
MRDA_DATA_DIR= os.path.join(MEDIA_DIR, 'mrda')

data_dir = '/Users/atherashraf/Documents/data'

env_path = os.path.join(CONFIG_DIR, ".env")
load_dotenv(env_path)

DATABASES = {
    "drm": {
        "ENGINE": "postgresql+psycopg2",
        "NAME": "drm",
        "USER": "dafast",
        "PASSWORD": "gAAAAABoQpUNv0nRVWIaukDZUYf2S2y1vSjJv_xTMp8GHgbrW2zc2gzjb9ls0HWLmNWWiafYabVCuGNsziooGU4xWCHu0VL3gw==",
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": "5432",
    }
}