import json
from urllib.request import urlopen
import os, ssl

'''This file was used to create a different "database" (JSON file) structure, and is not needed. Leaving here for use during future transformations.'''

# the ssl certificate validation stopped working for apeopelscalendar.org on 9-30
# below is a fix, however it is insecure and should be temporary
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

f = urlopen("https://www.apeoplescalendar.org/eventLibrary.json")
eventLibrary = json.load(f)
flattenedEventLibrary = {}

listOfDays = eventLibrary.keys()
eventCategories = [
  'Revolution',
  'Rebellion',
  'Labor',
  'Birthdays',
  'Assassinations',
  'Other',
]

# create function that regexs date string and gets numeric day month year
# datetime.datetime(2020, 5, 17)
# match year by doing all numbers before end of line, converting to int
# match day by getting all numbers between the first space and comma, converting to int
# get month number by taking first word and matching it against dictionary values (January: 1, February: 2, etc.)
# what format does the string need to take? maybe don't do this now, actually, save for a later MR

for day in listOfDays:
    currentDay = eventLibrary[day]
    if day not in flattenedEventLibrary.keys():
        flattenedEventLibrary[day] = []
    for category in eventCategories:
        categoryEvents = currentDay[category]
        for event in categoryEvents:
            if (event['description']):
                newEvent = event
                if newEvent['imgSrc'] == '/assets/eventPhotos/empty.jpg':
                    newEvent['imgSrc'] = ''
                flattenedEventLibrary[day].append(newEvent)

with open('eventLibrary.json', 'w') as outfile:
    json.dump(flattenedEventLibrary, outfile, indent = 2)