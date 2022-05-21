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
from nltk.tokenize import sent_tokenize

#authenticate with the twit
auth = tweepy.OAuthHandler(twitterApiKey, twitterApiSecretKey)
auth.set_access_token(twitterAccessToken, twitterAccessTokenSecret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# this is copied from the front end repository apc-web, generates URLs for specific events
def stringToSlug(str):
    #credit to https://gist.github.com/codeguy/6684588
    str = re.sub('^\s+|\s+$', '', str)
    str = str.lower()

    #remove accents, swap ñ for n, etc
    from_ = "àáäâèéëêìíïîòóöôōùúüûñç·/_,:;"
    to = "aaaaeeeeiiiiooooouuuunc------"
    for i in range(0, len(from_)):
        str = re.sub(from_[i], to[i], str)

    str = re.sub('[^a-z0-9 -]', '', str) #remove invalid chars
    str = re.sub('\s+', '-', str) #collapse whitespace and replace by -
    str = re.sub('-+', '-', str) #collapse dashes

    return str

# todayEvents: apcEvent[], testMode: boolean
def postEventsToTwitter(todayEvents, testMode):
    for apcEvent in todayEvents:
        tweetBody, title, description, imgSrc, NSFW, imgAltText = itemgetter('otd', 'title', 'description', 'imgSrc', 'NSFW', 'imgAltText')(apcEvent)
        # do the submit stuff for every event in the category
        slugifiedEventName = stringToSlug(title)
        if len(tweetBody) > 238:
            print (tweetBody)
            print('tweet too long! please shorten otd statement in database and try again')
            return
        tweetBody += " https://www.apeoplescalendar.org/calendar/events/" + slugifiedEventName

        print('posting tweet:')
        print(tweetBody[:240])
        print('\n')

        if not testMode:
            topLevelTweet = ''
            # if we have image
            if imgSrc:
                url = 'https://www.apeoplescalendar.org{}'.format(imgSrc)
                imgTuple = urllib.request.urlretrieve(url)
                image = imgTuple[0]
                try:
                    media = api.media_upload(image)
                    api.create_media_metadata(media.media_id, alt_text=imgAltText)
                    topLevelTweet = api.update_status(status=tweetBody, media_ids=[media.media_id], possibly_sensitive=NSFW)
                except:
                    # bug in the Tweepy where some image files can't be found
                    # just do the description
                    print('posting event photo to twitter caused error, posting text instead')
                    topLevelTweet = api.update_status(status=tweetBody, possibly_sensitive=NSFW)
            else:
                #if no image, just do the description
                topLevelTweet = api.update_status(status=tweetBody, possibly_sensitive=NSFW)
            try:
                postDescriptionThread(topLevelTweet.id, description)
            except Exception as e:
                print('something horrible happened when trying to post description thread:')
                print(tweetBody)
                print(e)

# this function breaks down the event description by comma,
# then builds up and posts an array of tweets in the form of a thread
def postDescriptionThread(initialTweetId, description):
    # break down description by comma (some sentences could be longer than 240 characters)
    descriptionSentences = sent_tokenize(description)
    descriptionByComma = []
    for index, sentence in enumerate(descriptionSentences):
        # many event descriptions repeat the on this day sentence in the original tweet
        # if first sentence contains an on this day statement, don't use it
        if index == 0 and re.search('(O|o)n this day', sentence):
            continue
        paddedSentence = '%s ' % (sentence)
        # split sentences by comma that isn't part of number (i.e., not 1,234)
        splitByComma = re.split(r',(?!/d)', paddedSentence)
        # add comma delimiter back in. if you can't understand this either, blame orestisf on stackoverflow
        withCommaAddedBackIn = [substr + ',' for substr in splitByComma[:-1]] + [splitByComma[-1]]
        for clause in withCommaAddedBackIn:
            descriptionByComma.append(clause)

    descriptionTweets = []
    nextTweet = '@apeoplescal '
    for index, clause in enumerate(descriptionByComma):
        onLastClause = index == len(descriptionByComma) - 1
        nextTweetWithClause = '%s%s' % (nextTweet, clause)
        # if too big for a tweet, push the current nextTweet to array and set up the next tweet
        if len(nextTweetWithClause) > 252:
            descriptionTweets.append(nextTweet)
            nextTweet = '@apeoplescal %s' % (clause)
            # if we had to reset nextTweet and we're on last clause, we need to append here, as elif will not be hit
            if onLastClause:
                descriptionTweets.append(nextTweetWithClause)
        # if we are on the last clause, append it to the list
        elif onLastClause:
            descriptionTweets.append(nextTweetWithClause)
        # reset nextTweet and build up until we hit character limit or end of clause list again
        else:
            nextTweet = nextTweetWithClause

    currentTweetIdToReplyTo = initialTweetId
    try:
        for tweet in descriptionTweets:
            currentTweet = api.update_status(tweet, in_reply_to_status_id=currentTweetIdToReplyTo)
            currentTweetIdToReplyTo = currentTweet.id
    except Exception as e:
        print('something horrible happened when trying to post description thread:')
        print(e)

