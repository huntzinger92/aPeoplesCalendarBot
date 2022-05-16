import json
from urllib.request import urlopen
import json
from utils.getDateFromUser import getDateFromUser
from utils.getTestModeFromUser import getTestModeFromUser
from postEventsToReddit import postEventsToReddit
from postEventsToTwitter import postEventsToTwitter
import os, ssl

# the ssl certificate validation stopped working for apeopelscalendar.org on 9-30
# below is a fix, however it is insecure and should be temporary
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

f = urlopen("https://www.apeoplescalendar.org/eventLibrary.json")
eventLibrary = json.load(f)

todayString = getDateFromUser()

testMode = getTestModeFromUser()

# get selected day's events
todayEvents = eventLibrary[todayString]

postEventsToReddit(todayEvents, todayString, testMode)

postEventsToTwitter(todayEvents, testMode)
