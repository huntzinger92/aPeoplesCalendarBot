import json
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

'''This file was used to create a different "database" (JSON file) structure, and is not needed. Leaving here for use during future transformations.'''

#get events from event library json file
with open('../txtLibrary.txt', encoding="utf8") as f:
  allEvents = json.load(f)

# constants
listOfDays = allEvents.keys()
eventCategories = [
  'Revolution',
  'Rebellion',
  'Labor',
  'Birthdays',
  'Assassinations',
  'Other',
]

def findOTDString(desc):
    if not desc:
        return desc
    otdString = ''
    sentenceList = sent_tokenize(desc)
    #find sentence with "on this day" in it. If too long, use first sentence that does not begin with an asterisk
    for sentence in sentenceList:
        if 'this day' in sentence:
            otdString = sentence
            break
    if not otdString:
        if sentenceList[0][0] != "*":
            print('sentence rejected')
            #sent_tokenize occasionaly includes two sentences
            firstSentenceNewLineSplit = sentenceList[0].split('\n\n')
            otdString = firstSentenceNewLineSplit[0]
        else:
            otdString = sentenceList[1]
    print('writing this as otdString:')
    print(otdString)
    return otdString

newEvents = {}

for day in listOfDays:
    newEvents[day] = {}
    currentDay = allEvents[day]
    for category in eventCategories:
        newEvents[day][category] = []
        categoryEvents = currentDay[category]
        for event in categoryEvents:
            print('event')
            print(event.keys())
            print(event['category'])
            print(event['date'])
            onThisDayString = findOTDString(event['description'])
            newEvents[day][category].append({
                'category': event['category'],
                'date': event['date'],
                'title': event['title'],
                'imgSrc': event['imgSrc'],
                'description': event['description'],
                'link': event['link'],
                'infoSrc': event['infoSrc'],
                'imgAltText': '',
                'NSFW': False,
                'otd': onThisDayString,
            })

with open('eventLibrary.json', 'w') as outfile:
    json.dump(newEvents, outfile, indent = 2)