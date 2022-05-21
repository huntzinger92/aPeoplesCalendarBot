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

otdStatement = "Earl Russell Browder, born on this day in 1891, was an American political activist, author, and well-known leader within the Communist Party USA (CPUSA), serving as its General Secretary from 1930 to 1945."

longDescription = "Earl Russell Browder, born on this day in 1891, was an American political activist, author, and well-known leader within the Communist Party USA (CPUSA), serving as its General Secretary from 1930 to 1945.\n\nBrowder's primary political rival within the Party was William Z. Foster; the two sharply disagreed on what the organization's stance towards the Roosevelt administration should be. Foster was the more radical of the two, while Browder endorsed Roosevelt's \"New Deal\", offering critical support to his administration.\n\nBrowder was the chairman of CPUSA when the Molotov-Ribbentrop Pact (an agreement of non-aggression between the Soviet and Nazi governments), and the Party quickly changed from being militantly anti-fascist to only engaging in moderate criticism of Germany. CPUSA's membership declined by 15% in the following year.\n\nBrowder was an advocate for a cooperative relationship between the Soviet Union and the United States after World War II, and was sharply criticized for this by the French Communist Party, later revealed to have done so on orders from Moscow in the \"Duclos Letter\".\n\nDue to the domestic Red Scare in the U.S. and Browder's ambitions clashing with the Soviet agenda, Browder was expelled from the Communist Party on February 5th, 1946."

def twitterTest():
    # url = 'https://www.apeoplescalendar.org/assets/eventPhotos/Individuals/alexandraKollontai.jpg'
    # imgTuple = urllib.request.urlretrieve(url)
    # image = imgTuple[0]
    # media = api.media_upload(image)
    # initialTweet = api.update_status(otdStatement, media_ids=[media.media_id])

    # break down description by comma (some sentences could be longer than 240 characters)
    descriptionSentences = sent_tokenize(longDescription)
    # print('descriptionSentences')
    # print(descriptionSentences)
    descriptionByComma = []
    for index, sentence in enumerate(descriptionSentences):
        # many event descriptions repeat the on this day sentence in the original tweet
        # if first sentence contains an on this day statement, don't use it
        if index == 0 and re.search('(O|o)n this day', sentence):
            continue
        paddedSentence = '%s ' % (sentence)
        splitByComma = paddedSentence.split(',')
        # if you can't understand this either, blame orestisf on stackoverflow
        withCommaAddedBackIn = [substr + ',' for substr in splitByComma[:-1]] + [splitByComma[-1]]
        for clause in withCommaAddedBackIn:
            descriptionByComma.append(clause)
    # print('descriptionByComma')
    # print(descriptionByComma)

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