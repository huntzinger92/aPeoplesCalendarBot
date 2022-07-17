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

otdStatement = "On this day in 2014, Eric Garner was murdered by the NYPD, choked to death after police suspected him of selling loose cigarettes. Garner said \"I can't breathe\" 11 times before dying. The man who filmed his death was poisoned in prison."

longDescription = "On this day in 2014, Eric Garner was murdered by the NYPD, choked to death after police suspected him of selling loose cigarettes. Garner said \"I can't breathe\" 11 times before dying. The man who filmed his death was poisoned in prison.\n\nEric Garner (1970 - 2014) was a former horticulturist at the New York City Department of Parks and Recreation, father of six, and grandfather of three. On July 17th, 2014, was approached by Justin D'Amico, a plainclothes officer, in front of a beauty supply store in Tompkinsville, Staten Island. D'Amico suspected Garner of selling loose cigarettes.\n\nGarner stated \"Every time you see me, you want to mess with me. I'm tired of it. It stops today...I'm minding my business, officer, I'm minding my business. Please just leave me alone. I told you the last time, please just leave me alone.\"\n\nAfter refusing to be handcuffed, 29-year old officer Daniel Pantaleo put Garner in an ultimately fatal chokehold. Despite Garner stating \"I can't breathe\" eleven times before losing consciousness, the several officers on scene did nothing to help him.\n\nRamsey Orta, a member of Copwatch, filmed the incident. Following a campaign of police harassment after the video went viral, he was arrested on weapons charges.\n\nBefore being imprisoned in Rikers, Orta claims a cop told him he'd be better off killing himself before being jailed. While in prison, Orta was poisoned by prison staff and at one point only ate food that his wife brought him. In May 2020, Orta was released from Groveland Correctional Facility.\n\nGarner's death was protested internationally and became one of many police killings protested within the Black Lives Matter movement. Some perpetrators of violence against police have cited Garner's murder as a motive.\n\nA grand jury elected to not indict Pantaleo on December 3rd, 2014. After the decision, Garner's widow was asked whether she accepted Pantaleo's condolences. She replied: \"Hell, no! The time for remorse would have been when my husband was yelling to breathe...No, I don't accept his apology. No, I could care less about his condolences...He's still working. He's still getting a paycheck. He's still feeding his kids, when my husband is six feet under and I'm looking for a way to feed my kids now.\"\n\nA New York Police Department disciplinary hearing regarding Pantaleo's treatment of Garner was held in the summer of 2019; Pantaleo was fired on August 19, 2019, more than five years after he murdered Garner."

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
    descriptionSentencesWithLineBreak = []
    currentSentenceIsPartOfQuote = False
    for index, sentence in enumerate(descriptionSentences):
        # many event descriptions repeat the on this day sentence used in the original tweet
        # if first sentence contains an on this day statement, don't use it in the description
        if index == 0 and re.search('(O|o)n this day', sentence):
            continue
        descriptionSentencesWithLineBreak.append(sentence)
        # print(sentence)
        sentenceOpensOrClosesQuote = sentence.count('"') % 2 != 0
        # print('sentenceOpensOrClosesQuote', sentenceOpensOrClosesQuote)
        if sentenceOpensOrClosesQuote:
            currentSentenceIsPartOfQuote = not currentSentenceIsPartOfQuote
        isLastSentence = index == len(descriptionSentences) - 1
        # print('currentSentenceIsPartOfQuote', currentSentenceIsPartOfQuote)
        shouldAddLineBreak = not currentSentenceIsPartOfQuote and not isLastSentence
        # print('shouldAddLineBreak', shouldAddLineBreak)
        if shouldAddLineBreak:
            descriptionSentencesWithLineBreak.append('\n')
    print('descriptionSentencesWithLineBreak')
    print(descriptionSentencesWithLineBreak)
    # break down description by comma (some sentences could be longer than 240 characters)
    descriptionByComma = []
    for index, sentence in enumerate(descriptionSentencesWithLineBreak):
        # if any of the first two sentences (including new line between them) duplicate something in the otd statement, don't use it in the description
        # if index < 3:
            # print(sentence)
            # print(sentence in otdStatement)
        if index < 3 and sentence in otdStatement:
            continue
        paddedSentence = '%s ' % (sentence)
        # split sentences by comma that isn't part of number (i.e., don't split 1,234)
        splitByComma = re.split(r',(?!\d)', paddedSentence)
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