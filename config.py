import os
import datetime

from dotenv import load_dotenv

try:
    postgres = os.environ['DATABASE_URL']
    token = os.environ['TOKEN']
    print("time is ", datetime.datetime.now())
    print('loaded heroku env variables')
except KeyError:
    load_dotenv()
    print('loaded local dotenv file')
    postgres = os.environ['POSTGRES']
    token = os.environ['token']
    guild = os.environ['guild']
    log_channel = os.environ['log_channel']
    announcement = os.environ['announcement']
cogs = ["cogs.reminder", "cogs.help", 'cogs.misc', 'cogs.management']