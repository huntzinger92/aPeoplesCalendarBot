import tweepy
import re
# env variables for social media authentication
from env import twitterApiKey
from env import twitterApiSecretKey
# from env import twitterBearerToken
from env import twitterAccessToken
from env import twitterAccessTokenSecret
import os, ssl
from nltk.tokenize import sent_tokenize

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

#authenticate with the twit
auth = tweepy.OAuthHandler(twitterApiKey, twitterApiSecretKey)
auth.set_access_token(twitterAccessToken, twitterAccessTokenSecret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

otdStatement = "The Indian Removal Act, signed into law on this day in 1830, provided the legal authority for the president to force indigenous peoples west of the Mississippi River, leading to the \"Trail of Tears\", which killed more than 10,000."

longDescription = "The Indian Removal Act, signed into law on this day in 1830, provided the legal authority for the president to force indigenous peoples west of the Mississippi River, leading to the \"Trail of Tears\", which killed more than 10,000.\n\nThe law is an example of the systematic genocide brought against indigenous peoples by the U.S. government because it discriminated against them in such a way as to effectively guarantee the death of vast numbers of their population. The Act was signed into law by Andrew Jackson and was strongly enforced by his and his successors' administrations.\n\nThe enforcement of the Indian Removal Act directly led to the \"Trail of Tears\", which killed over 10,000 indigenous peoples. Although some tribes left peacefully, others fought back, leading to the Second Seminole War of 1835."

def twitterTest():
    # url = 'https://www.apeoplescalendar.org/assets/eventPhotos/Individuals/alexandraKollontai.jpg'
    # imgTuple = urllib.request.urlretrieve(url)
    # image = imgTuple[0]
    # media = api.media_upload(image)
    # initialTweet = api.update_status(otdStatement, media_ids=[media.media_id])

    # break down description into sentences
    descriptionSentences = sent_tokenize(longDescription)
    # print('descriptionSentences')
    # print(descriptionSentences)
    # break down description by comma (some sentences could be longer than 240 characters)
    descriptionByComma = []
    for index, sentence in enumerate(descriptionSentences):
        # many event descriptions repeat the on this day sentence used in the original tweet
        # if first sentence contains an on this day statement, don't use it in the description
        if index == 0 and re.search('(O|o)n this day', sentence):
            continue
        # if any of the first three sentences duplicate something in the otd statement, don't use it in the description
        if index < 3:
            print(sentence)
            print(sentence in otdStatement)
        if index < 3 and sentence in otdStatement:
            continue
        paddedSentence = '%s ' % (sentence)
        # split sentences by comma that isn't part of number (i.e., don't split 1,234)
        splitByComma = re.split(r',(?!\d)', paddedSentence)
        # if you can't understand this either, blame orestisf on stackoverflow
        withCommaAddedBackIn = [substr + ',' for substr in splitByComma[:-1]] + [splitByComma[-1]]
        for clause in withCommaAddedBackIn:
            descriptionByComma.append(clause)
    print('descriptionByComma')
    print(descriptionByComma)

    descriptionTweets = []
    nextTweet = '@apeoplescal '
    for index, clause in enumerate(descriptionByComma):
        # print('clause:')
        # print(clause)
        onLastClause = index == len(descriptionByComma) - 1
        nextTweetWithClause = '%s%s' % (nextTweet, clause)
        # if too big for a tweet, push the current nextTweet to array and set up the next tweet
        if len(nextTweetWithClause) > 252:
            print(nextTweet)
            print('\n')
            descriptionTweets.append(nextTweet)
            nextTweet = '@apeoplescal %s' % (clause)
            # if we had to reset nextTweet and we're on last clause, we need to append here, as elif will not be hit
            if onLastClause:
                print(nextTweet)
                print('\n')
                descriptionTweets.append(nextTweet)
        # if we are on the last clause, append it to the list
        elif onLastClause:
            print(nextTweet)
            print('\n')
            descriptionTweets.append(nextTweetWithClause)
        # reset nextTweet and build up until we hit character limit or end of clause list again
        else:
            nextTweet = nextTweetWithClause

    # print('descriptionTweets')
    # print(descriptionTweets)

    # currentTweetIdToReplyTo = initialTweet.id
    # try:
    #     for tweet in descriptionTweets:
    #         currentTweet = api.update_status(tweet, in_reply_to_status_id=currentTweetIdToReplyTo)
    #         currentTweetIdToReplyTo = currentTweet.id
    # except Exception as e:
    #     print('something horrible happened when trying to post description thread:')
    #     print(e)

twitterTest()