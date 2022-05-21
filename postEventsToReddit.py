import praw
import urllib.request
from operator import itemgetter
import re
from env import reddit_client_id
from env import reddit_client_secret
from env import reddit_user_agent
from env import reddit_username
from env import reddit_password

# these flair ids come from the subreddit /r/apeoplescalendar
flairDict = {'Revolution': '17b5077c-f839-11ea-821f-0e8aea2b85cf', 'Rebellion': '2779cdf0-f839-11ea-8778-0ea18488d07b', 'Labor': '2e06b778-f839-11ea-86f0-0e597e755ef5', 'Birthdays': '356475be-f839-11ea-aa42-0e7cce3a2b57', 'Assassinations': '3d531a5a-f839-11ea-a5ab-0e8a96a82b05', 'Other': '42dbbda6-f839-11ea-8ecd-0ee109f75723'}

apcSubredditName = 'aPeoplesCalendar'

reddit = praw.Reddit(client_id=reddit_client_id,
                     client_secret=reddit_client_secret,
                     user_agent=reddit_user_agent,
                     username=reddit_username,
                     password=reddit_password)

# todayEvents: eventObjs[], testMode: boolean
def postEventsToReddit(todayEvents, todayString, testMode):
    if testMode:
        for apcEvent in todayEvents:
            title = apcEvent['otd']
            print ('reddit post title:')
            print(title)
            print('\n')
        return
    else:
        postedEvents = submitEvents(todayEvents, todayString)
        submitComments(postedEvents, todayString)


# todayEvents: eventObjs[]
def submitEvents(todayEvents, todayString):
    # a list of posted events, used by comment posting function to find the thread to comment on
    eventList = []
    for apcEvent in todayEvents:
        otd, imgSrc, category, NSFW = itemgetter('otd', 'imgSrc', 'category', 'NSFW')(apcEvent)
        if imgSrc:
            imgUrl = 'https://www.apeoplescalendar.org{}'.format(imgSrc)
            imgTuple = urllib.request.urlretrieve(imgUrl)
            image = imgTuple[0]
            try:
                reddit.subreddit("aPeoplesCalendar").submit_image(otd, image, flair_id=flairDict[category], nsfw=NSFW)
            except Exception as e:
                print(otd)
                print("photo won't load, creating a self text post")
                print("Error:")
                print(e)
                selfText = formatDescription(apcEvent, todayString)
                reddit.subreddit(apcSubredditName).submit(otd, selftext=selfText, flair_id=flairDict[category],  nsfw=NSFW)
        else:
            #selftext submission when no image
            selfText = formatDescription(apcEvent, todayString)
            reddit.subreddit(apcSubredditName).submit(otd, selftext=selfText, flair_id=flairDict[category],  nsfw=NSFW)
        eventList.append((apcEvent, otd))
    return eventList

def formatDescription(apcEvent, todayString):
    title, infoSrc, link, imgAltText, description = itemgetter('title', 'infoSrc', 'link', 'imgAltText', 'description')(apcEvent)
    # create the on this day link to the website, used within the event description:
    otdLink = "https://www.apeoplescalendar.org/calendar/day/%s" % (todayString)
    otdIndex = description.find("On this day")
    if otdIndex != -1:
        description = description[:otdIndex] + '[On this day](' + otdLink + ')' + description[otdIndex + 11:]
    else:
        otdIndex = description.find("on this day")
        if otdIndex != -1:
            description = description[:otdIndex] + '[on this day](' + otdLink + ')' + description[otdIndex + 11:]

    # check for pdf links, create warnings if needed
    pattern = '\.pdf$'
    pdfWarning1 = ' (PDF Warning)' if re.search(pattern, infoSrc) else ''
    pdfWarning2 = ' (PDF Warning)' if re.search(pattern, link) else ''

    # create image transcription message
    imageTranscriptionMessage = ''
    # if we have image
    if imgAltText:
        imageTranscriptionMessage = '''\n\n**Image Transcription**: %s''' % (imgAltText)
    else:
        imageTranscriptionMessage = '''\n\n**Image Transcription**: Looks like we don't have an image caption for this event yet. Feel free to suggest one below.''' 
    # format the comment using data from the apcEvent object
    body = '''**%s**%s\n\n%s\n\nRead more:\n\n%s%s\n\n%s%s''' % (title, imageTranscriptionMessage, description, infoSrc, pdfWarning1, link, pdfWarning2)
    return body

def submitComment(postedEvent, todayString):
    # find matching submission within the last twenty threads in the subreddit
    for submission in reddit.subreddit(apcSubredditName).new(limit=20):
        if submission.title == postedEvent[1]:
            # self posts already have full event description, only comment description on events with images
            if not submission.is_self:
                print('adding comment to post with title: ' + submission.title)
                correctPost = reddit.submission(id=submission.id)
                # create the on this day link within the event description:
                body = formatDescription(postedEvent[0], todayString)
                # make the post reply
                correctPost.reply(body)

def submitComments(postedEvents, todayString):
    for postedEvent in postedEvents:
        submitComment(postedEvent, todayString)