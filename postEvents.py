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

# THIS IS THE OLD, FUNCTIONAL REDDIT POSTING, MOVED TO postEventsToReddit.py
# #reddit posting first
# reddit = praw.Reddit(client_id=reddit_client_id,
#                      client_secret=reddit_client_secret,
#                      user_agent=reddit_user_agent,
#                      username=reddit_username,
#                      password=reddit_password)

# #holds tuples of event object and title for comment function to find
# eventList = []

# flairDict = {'Revolution': '17b5077c-f839-11ea-821f-0e8aea2b85cf', 'Rebellion': '2779cdf0-f839-11ea-8778-0ea18488d07b', 'Labor': '2e06b778-f839-11ea-86f0-0e597e755ef5', 'Birthdays': '356475be-f839-11ea-aa42-0e7cce3a2b57', 'Assassinations': '3d531a5a-f839-11ea-a5ab-0e8a96a82b05', 'Other': '42dbbda6-f839-11ea-8ecd-0ee109f75723',}

# def submitEvents():
#     for event_ in todayEvents:
#         #do the submit stuff for every event in the category)
#         #first, create title
#         title = event_['otd']
#         if testMode != 'n':
#             print(title)
#         else:
#             if event_['imgSrc']:
#                 url = 'https://www.apeoplescalendar.org{}'.format(event_['imgSrc'])
#                 imgTuple = urllib.request.urlretrieve(url)
#                 image = imgTuple[0]
#                 # image = 'https://www.apeoplescalendar.org{}'.format(event_['imgSrc'])
#                 try:
#                     reddit.subreddit("aPeoplesCalendar").submit_image(title, image, flair_id=flairDict[event_['category']], nsfw=event_['NSFW'])
#                 except Exception as e:
#                     print(title)
#                     print("photo won't load, creating a self text post")
#                     print("Error:")
#                     print(e)
#                     selfText = formatDescription(event_)
#                     reddit.subreddit("aPeoplesCalendar").submit(title, selftext=selfText, flair_id=flairDict[event_['category']],  nsfw=event_['NSFW'])
#             else:
#                 #selftext submission
#                 selfText = formatDescription(event_)
#                 reddit.subreddit("aPeoplesCalendar").submit(title, selftext=selfText, flair_id=flairDict[event_['category']],  nsfw=event_['NSFW'])
#             #append event_ to list of events, used for making comments
#             eventList.append((event_, title))

# def formatDescription(event_):
#     #create the on this day link within the event description:
#     otdLink = "https://www.apeoplescalendar.org/calendar/day/%s" % (todayString)
#     newDescription = event_['description']
#     otdIndex = newDescription.find("On this day")
#     if otdIndex != -1:
#         newDescription = newDescription[:otdIndex] + '[On this day](' + otdLink + ')' + newDescription[otdIndex + 11:]
#     else:
#         otdIndex = newDescription.find("on this day")
#         if otdIndex != -1:
#             newDescription = newDescription[:otdIndex] + '[on this day](' + otdLink + ')' + newDescription[otdIndex + 11:]
#     pattern = '\.pdf$'
#     pdfWarning1 = ' (PDF Warning)' if re.match(pattern, event_['infoSrc']) else ''
#     pdfWarning2 = ' (PDF Warning)' if re.match(pattern, event_['link']) else ''
#     imageTranscriptionMessage = ''
#     #if we have image
#     if event_['imgSrc']:
#         if event_['imgAltText']:
#             imageTranscriptionMessage = '''\n\n**Image Transcription**: %s''' % (event_['imgAltText'])
#         else:
#             imageTranscriptionMessage = '''\n\n**Image Transcription**: Looks like we don't have an image caption for this event yet. Feel free to suggest one below.''' 
#     #format the comment using data from the event_ object
#     body = '''**%s**%s\n\n%s\n\n[Main Source](%s)%s\n\n[More Info](%s)%s''' % (event_['title'], imageTranscriptionMessage, newDescription, event_['infoSrc'], pdfWarning1, event_['link'], pdfWarning2)
#     return body

# def submitComment(eventSubmission):
#     #get the matching submission
#     #TO DO: rather than searching among last twenty posts, can probably just find it by passing thread ID to the eventList, i.e. (eventObject, threadID)
#     #without doing that, if you have more than 20 submissions on a single day, comment will miss it
#     for submission in reddit.subreddit("aPeoplesCalendar").new(limit=20):
#         if submission.title == eventSubmission[1]:
#             if not submission.is_self:
#                 print('adding comment to post with title: ' + submission.title)
#                 correctPost = reddit.submission(id=submission.id)
#                 #create the on this day link within the event description:
#                 body = formatDescription(eventSubmission[0])
#                 #make the post reply
#                 correctPost.reply(body)

# submitEvents()

# if testMode == 'n':
#     for event_ in eventList:
#         submitComment(event_)

# BELOW IS THE OLD FUNCTIONAL STUFF FOR POSTING TO TWITTER, HAS BEEN MOVED TO postEventsToTwitter.py

postEventsToTwitter(todayEvents, testMode)

# #authenticate with the twit
# auth = tweepy.OAuthHandler(twitterApiKey, twitterApiSecretKey)
# auth.set_access_token(twitterAccessToken, twitterAccessTokenSecret)

# api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# def stringToSlug(str):
#     #credit to https://gist.github.com/codeguy/6684588
#     str = re.sub('^\s+|\s+$', '', str)
#     str = str.lower();

#     #remove accents, swap ñ for n, etc
#     from_ = "àáäâèéëêìíïîòóöôōùúüûñç·/_,:;";
#     to = "aaaaeeeeiiiiooooouuuunc------";
#     for i in range(0, len(from_)):
#         str = re.sub(from_[i], to[i], str)

#     str = re.sub('[^a-z0-9 -]', '', str) #remove invalid chars
#     str = re.sub('\s+', '-', str) #collapse whitespace and replace by -
#     str = re.sub('-+', '-', str) #collapse dashes

#     return str

# def submitEvents():
#             for event_ in todayEvents:
#                 body = event_['otd']
#                 #do the submit stuff for every event in the category
#                 slugifiedEventName = stringToSlug(event_['title'])
#                 if len(body) > 238:
#                     print('tweet too long!')
#                 body += " https://www.apeoplescalendar.org/calendar/events/" + slugifiedEventName
#                 #body += "https://www.apeoplescalendar.org/events/" + slugifiedEventName
#                 print(body[:240])
#                 print('\n')
#                 if testMode == 'n':
#                     #if we have image
#                     if event_['imgSrc']:
#                         url = 'https://www.apeoplescalendar.org{}'.format(event_['imgSrc'])
#                         imgTuple = urllib.request.urlretrieve(url)
#                         image = imgTuple[0]
#                         #image = 'https://www.apeoplescalendar.org{}'.format(event_['imgSrc'])
#                         try:
#                             media = api.media_upload(image)
#                             api.update_status(status=body, media_ids=[media.media_id])
#                         except:
#                             #bug in the Tweepy where some image filetypes can't be found
#                             #just do the description
#                             print('posting event photo to twitter caused error, posting text instead')
#                             api.update_status(status=body)
#                     else:
#                         #if no image, just do the description
#                         api.update_status(status=body)

# submitEvents()
