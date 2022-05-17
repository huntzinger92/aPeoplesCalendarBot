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

otdStatement = "On this day in 1871, the Paris Commune, a hotbed of radical working class politics and watershed moment in revolutionary anti-capitalist history, was crushed by French Army."

longDescription = "On this day in 1871, the Paris Commune, a hotbed of radical working class politics and watershed moment in revolutionary anti-capitalist history, was crushed by French Army. 20,000 people were killed and 44,000 arrested. The Paris Commune was a radical socialist government that had formed in Paris a few months earlier, on March 18th, 1871. The government of the Paris Commune developed a set of progressive, secular, and social democratic policies, although its existence was too brief to implement all of them. Among these policies were the separation of church and state, abolition of child labor, abolishment of interest on some forms of debt, as well as the right of employees to take over and run an enterprise if it was deserted by its original owner. The commune was attacked by the French National Army on May 21st, 1871, beginning the so-called \"Bloody Week\", which defeated the revolutionary movement. After crushing the rebellion, the French government imprisoned approximately 44,000 people for their role in the uprising. Estimated deaths from the fighting are around 20,000. The Paris Commune was analyzed by many communist thinkers, most notably Karl Marx, who called it a \"dictatorship of the proletariat.\" Vladimir Lenin danced in the snow when the newly formed Bolshevik government lasted longer than the Paris Commune. The episode inspired similar revolutionary attempts around the world, including in Moscow (1905), Petrograd (1917), and Shanghai (1927 and 1967)."

def twitterTest():
    # url = 'https://www.apeoplescalendar.org/assets/eventPhotos/Individuals/alexandraKollontai.jpg'
    # imgTuple = urllib.request.urlretrieve(url)
    # image = imgTuple[0]
    # media = api.media_upload(image)
    # initialTweet = api.update_status(otdStatement, media_ids=[media.media_id])

    # break down description by comma (some sentences could be longer than 240 characters)
    descriptionSentences = sent_tokenize(longDescription)
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

    # currentTweetIdToReplyTo = initialTweet.id
    # try:
    #     for tweet in descriptionTweets:
    #         currentTweet = api.update_status(tweet, in_reply_to_status_id=currentTweetIdToReplyTo)
    #         currentTweetIdToReplyTo = currentTweet.id
    # except Exception as e:
    #     print('something horrible happened when trying to post description thread:')
    #     print(e)

twitterTest()