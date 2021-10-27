import tweepy
import re
import urllib.request
from operator import itemgetter
# env variables for social media authentication
from env import twitterApiKey
from env import twitterApiSecretKey
# from env import twitterBearerToken
from env import twitterAccessToken
from env import twitterAccessTokenSecret
from utils.getDateFromUser import getDateFromUser
from utils.getTestModeFromUser import getTestModeFromUser
from postEventsToReddit import postEventsToReddit

#authenticate with the twit
auth = tweepy.OAuthHandler(twitterApiKey, twitterApiSecretKey)
auth.set_access_token(twitterAccessToken, twitterAccessTokenSecret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# this is copied from the front end repository apc-web, generates URLs for specific events
def stringToSlug(str):
    #credit to https://gist.github.com/codeguy/6684588
    str = re.sub('^\s+|\s+$', '', str)
    str = str.lower();

    #remove accents, swap ñ for n, etc
    from_ = "àáäâèéëêìíïîòóöôōùúüûñç·/_,:;";
    to = "aaaaeeeeiiiiooooouuuunc------";
    for i in range(0, len(from_)):
        str = re.sub(from_[i], to[i], str)

    str = re.sub('[^a-z0-9 -]', '', str) #remove invalid chars
    str = re.sub('\s+', '-', str) #collapse whitespace and replace by -
    str = re.sub('-+', '-', str) #collapse dashes

    return str

# todayEvents: apcEvent[], testMode: boolean
def postEventsToTwitter(todayEvents, testMode):
    for apcEvent in todayEvents:
        tweetBody, title, imgSrc = itemgetter('otd', 'title', 'imgSrc')(apcEvent)
        # do the submit stuff for every event in the category
        slugifiedEventName = stringToSlug(title)
        if len(tweetBody) > 238:
            print (tweetBody)
            print('tweet too long! please shorten otd statement in database and try again')
            return
        tweetBody += " https://www.apeoplescalendar.org/calendar/events/" + slugifiedEventName

        print('event tweet:')
        print(tweetBody[:240])
        print('\n')

        if not testMode:
            # if we have image
            if imgSrc:
                url = 'https://www.apeoplescalendar.org{}'.format(imgSrc)
                imgTuple = urllib.request.urlretrieve(url)
                image = imgTuple[0]
                try:
                    media = api.media_upload(image)
                    api.update_status(status=tweetBody, media_ids=[media.media_id])
                except:
                    # bug in the Tweepy where some image files can't be found
                    # just do the description
                    print('posting event photo to twitter caused error, posting text instead')
                    api.update_status(status=tweetBody)
            else:
                #if no image, just do the description
                api.update_status(status=tweetBody)
