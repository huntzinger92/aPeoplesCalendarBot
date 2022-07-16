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

otdStatement = "Assata Shakur, born on this day in 1947, is a revolutionary socialist and former member of the Black Liberation Army (BLA) who became the first woman to be added to the FBI's Most Wanted Terrorists list in 2013."

longDescription = "Assata Shakur, born on this day in 1947, is a revolutionary socialist and former member of the Black Liberation Army (BLA) who became the first woman to be added to the FBI's Most Wanted Terrorists list in 2013.\n\nShakur grew up in New York City and Wilmington, North Carolina. She became involved in political activism at Borough of Manhattan Community College and City College of New York, participating in sit-ins and civil rights protests.\n\nAfter graduating from college, Shakur briefly joined the Black Panther Party, leading its Harlem chapter. She left the Panthers and joined the Black Liberation Army, a black power group that was inspired by the Viet Cong and Algerian resistance movements and waged guerrilla warfare against the U.S. government from 1970 to 1981. Shakur was one of the targets of the FBI's COINTELPRO program.\n\nAfter being involved in a shootout with New Jersey police officers, Shakur was convicted on multiple counts of assault and murder and sentenced to life in prison. In 1979, BLA members freed her in a bloodless prison escape.\n\nShakur successfully sought political asylum in Cuba, where she still lives today.\n\n\"I didn't know what a fool they had made out of me until I grew up and started to read real history.\"\n\n- Assata Shakur"

def twitterTest():
    # url = 'https://www.apeoplescalendar.org/assets/eventPhotos/Individuals/alexandraKollontai.jpg'
    # imgTuple = urllib.request.urlretrieve(url)
    # image = imgTuple[0]
    # media = api.media_upload(image)
    # initialTweet = api.update_status(otdStatement, media_ids=[media.media_id])

    # break down description into sentences
    descriptionSentences = sent_tokenize(longDescription)
    print('descriptionSentences')
    print(descriptionSentences)
    descriptionSentencesWithLineBreak = []
    for index, sentence in enumerate(descriptionSentences):
        # many event descriptions repeat the on this day sentence used in the original tweet
        # if first sentence contains an on this day statement, don't use it in the description
        if index == 0 and re.search('(O|o)n this day', sentence):
            continue
        descriptionSentencesWithLineBreak.append(sentence)
        # don't add new lines after last sentence
        if index < len(descriptionSentences) - 1:
            descriptionSentencesWithLineBreak.append('\n\n')
    print('descriptionSentencesWithLineBreak')
    print(descriptionSentencesWithLineBreak)
    # break down description by comma (some sentences could be longer than 240 characters)
    descriptionByComma = []
    for index, sentence in enumerate(descriptionSentencesWithLineBreak):
        # if any of the first two sentences (including new line between them) duplicate something in the otd statement, don't use it in the description
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
        if len(nextTweetWithClause) > 244:
            # print(nextTweet)
            # print('\n')
            descriptionTweets.append(nextTweet)
            nextTweet = '@apeoplescal %s' % (clause)
            # if we had to reset nextTweet and we're on last clause, we need to append here, as elif will not be hit
            if onLastClause:
                # print(nextTweet)
                # print('\n')
                descriptionTweets.append(nextTweet)
        # if we are on the last clause, append it to the list
        elif onLastClause:
            # print(nextTweet)
            # print('\n')
            descriptionTweets.append(nextTweetWithClause)
        # reset nextTweet and build up until we hit character limit or end of clause list again
        else:
            nextTweet = nextTweetWithClause

    for tweet in descriptionTweets:
        print(tweet)

    # currentTweetIdToReplyTo = initialTweet.id
    # try:
    #     for tweet in descriptionTweets:
    #         currentTweet = api.update_status(tweet, in_reply_to_status_id=currentTweetIdToReplyTo)
    #         currentTweetIdToReplyTo = currentTweet.id
    # except Exception as e:
    #     print('something horrible happened when trying to post description thread:')
    #     print(e)

twitterTest()