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

# authenticate with the twit
auth = tweepy.OAuthHandler(twitterApiKey, twitterApiSecretKey)
auth.set_access_token(twitterAccessToken, twitterAccessTokenSecret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# this is copied from the front end repository apc-web, generates URLs for specific events


def stringToSlug(str):
    # credit to https://gist.github.com/codeguy/6684588
    str = re.sub('^\s+|\s+$', '', str)
    str = str.lower()

    # remove accents, swap ñ for n, etc
    from_ = "àáäâèéëêìíïîòóöôōùúüûñç·/_,:;"
    to = "aaaaeeeeiiiiooooouuuunc------"
    for i in range(0, len(from_)):
        str = re.sub(from_[i], to[i], str)

    str = re.sub('[^a-z0-9 -]', '', str)  # remove invalid chars
    str = re.sub('\s+', '-', str)  # collapse whitespace and replace by -
    str = re.sub('-+', '-', str)  # collapse dashes

    return str

def uploadPhoto(imgSrc):
    url = 'https://www.apeoplescalendar.org{}'.format(imgSrc)
    imgTuple = urllib.request.urlretrieve(url)
    image = imgTuple[0]
    try:
        media = api.media_upload(image)
    except Exception as error:
        raise Exception(error)
    return media

def postEventToTwitter(apcEvent):
    tweetBody, title, description, imgSrc, NSFW, imgAltText = itemgetter(
            'otd', 'title', 'description', 'imgSrc', 'NSFW', 'imgAltText')(apcEvent)
    slugifiedEventName = stringToSlug(title)
    tweetBody += " https://www.apeoplescalendar.org/calendar/events/" + slugifiedEventName

    topLevelTweet = ''
    media = False
    # if we have image
    if imgSrc:
        try:
            media = uploadPhoto(imgSrc)
        except Exception as error:
            print('could not upload image:')
            print(imgSrc)
            print(error)
            print(media)
            print('retrying image upload...')
            try:
                media = uploadPhoto(imgSrc)
            except Exception as error:
                print('could not upload image on 2nd attempt:')
                print(imgSrc)
                print(error)
                print(media)
                print('yeah, your image is fucked')
                        
        if imgAltText:
            try:
                api.create_media_metadata(
                    media.media_id, alt_text=imgAltText)
            except Exception as error:
                print('could not upload media metadata:')
                print(error)
                print('imgSrc:')
                print(imgSrc)

        try: topLevelTweet = api.update_status(status=tweetBody, media_ids=[
                                                media.media_id], possibly_sensitive=NSFW)
        except Exception as error:
            # bug in the Tweepy where some image files can't be found
            print(
                'posting event photo to twitter caused error, posting text instead')
            print(error)
            print('imgSrc:')
            print(imgSrc)
            # just do the description
            topLevelTweet = api.update_status(
                status=tweetBody, possibly_sensitive=NSFW)
    else:
        # if no image, just do the description
        topLevelTweet = api.update_status(
            status=tweetBody, possibly_sensitive=NSFW)
    try:
        postDescriptionThread(topLevelTweet.id, description, tweetBody)
    except Exception as e:
        print(
            'something horrible happened when trying to post description thread:')
        print(tweetBody)
        print(e)

def postEventsToTwitter(todayEvents, testMode):
    for apcEvent in todayEvents:
        otd = itemgetter('otd')(apcEvent)
        if len(otd) > 238:
            print(otd)
            print(
                'tweet too long! please shorten otd statement in database and try again')
            return

        print('posting tweet:')
        print(otd)
        print('\n')

        if not testMode:
            postEventToTwitter(apcEvent)

# this function breaks down the event description by comma,
# then builds up and posts an array of tweets in the form of a thread

def postDescriptionThread(initialTweetId, description, otdStatement):
    # break down description by comma (some sentences could be longer than 240 characters)
    descriptionSentences = sent_tokenize(description)
    descriptionSentencesWithLineBreak = []
    currentSentenceIsPartOfQuote = False
    for index, sentence in enumerate(descriptionSentences):
        # many event descriptions repeat the on this day sentence used in the original tweet
        # if first sentence contains an on this day statement, don't use it in the description
        if index == 0 and re.search('(O|o)n this day', sentence):
            continue
        descriptionSentencesWithLineBreak.append(sentence)
        # determine if we need to add a line break after this sentence
        sentenceOpensOrClosesQuote = sentence.count('"') % 2 != 0
        if sentenceOpensOrClosesQuote:
            currentSentenceIsPartOfQuote = not currentSentenceIsPartOfQuote
        isLastSentence = index == len(descriptionSentences) - 1
        shouldAddLineBreak = not currentSentenceIsPartOfQuote and not isLastSentence
        if shouldAddLineBreak:
            descriptionSentencesWithLineBreak.append('\n')

    descriptionByComma = []
    for index, sentence in enumerate(descriptionSentencesWithLineBreak):
        # if any of the first two sentences (including new line between them) duplicate something in the otd statement, don't use it in the description
        if index < 3 and sentence in otdStatement:
            continue
        paddedSentence = '%s ' % (sentence)
        # split sentences by comma that isn't part of number (i.e., don't split 1,234)
        splitByComma = re.split(r',(?!\d)', paddedSentence)
        # add comma delimiter back in. if you can't understand this either, blame orestisf on stackoverflow
        withCommaAddedBackIn = [
            substr + ',' for substr in splitByComma[:-1]] + [splitByComma[-1]]
        for clause in withCommaAddedBackIn:
            descriptionByComma.append(clause)

    descriptionTweets = []
    nextTweet = '@apeoplescal '
    for index, clause in enumerate(descriptionByComma):
        onLastClause = index == len(descriptionByComma) - 1
        nextTweetWithClause = '%s%s' % (nextTweet, clause)
        # if too big for a tweet, push the current nextTweet to array and set up the next tweet
        if len(nextTweetWithClause) > 244:
            descriptionTweets.append(nextTweet)
            nextTweet = '@apeoplescal %s' % (clause)
            # if we had to reset nextTweet and we're on last clause, we need to append here, as elif will not be hit
            if onLastClause:
                descriptionTweets.append(nextTweet)
        # if we are on the last clause, append it to the list
        elif onLastClause:
            descriptionTweets.append(nextTweetWithClause)
        # reset nextTweet and build up until we hit character limit or end of clause list again
        else:
            nextTweet = nextTweetWithClause

    currentTweetIdToReplyTo = initialTweetId
    try:
        for tweet in descriptionTweets:
            currentTweet = api.update_status(
                tweet, in_reply_to_status_id=currentTweetIdToReplyTo)
            currentTweetIdToReplyTo = currentTweet.id
    except Exception as e:
        print('something horrible happened when trying to post description thread:')
        print(e)
