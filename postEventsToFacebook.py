from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from operator import itemgetter
from time import sleep
import re
# import geckodriver_autoinstaller
import chromedriver_autoinstaller
from env import facebook_username
from env import facebook_password
import json
from urllib.request import urlopen
import json
from utils.getDateFromUser import getDateFromUser
from utils.getTestModeFromUser import getTestModeFromUser
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

email = facebook_username
password = facebook_password
# post = input('Enter your post: ')

# geckodriver_autoinstaller.install()
chromedriver_autoinstaller.install()

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

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

def login():
    driver.get('https://m.facebook.com/')
    email_input = driver.find_element(by=By.XPATH, value='//*[@id="m_login_email"]')
    email_input.send_keys(email)
    password_input = driver.find_element(by=By.XPATH, value='//*[@id="m_login_password"]')
    password_input.send_keys(password)
    login_btn = driver.find_element(by=By.NAME, value='login')
    login_btn.click()
    wait.until(EC.url_changes('https://m.facebook.com/'))

def postEvent(apcEvent):
    driver.get('https://m.facebook.com/')
    whats_on_your_mind = driver.find_element(by=By.XPATH, value='//*[text() = "What\'s on your mind?"]')
    # we need the parent of this element to actually post
    post_input = whats_on_your_mind.find_element(by=By.XPATH, value='..')
    post_input.click()
    # wait for input menu
    wait.until(EC.presence_of_element_located((By.ID, 'uniqid_1')))
    post_text_area = driver.find_element(by=By.XPATH, value='//*[@id="uniqid_1"]')
    # format event description
    description = formatDescription(apcEvent)
    post_text_area.send_keys(description)
    # wait for link preview - this is how we get the photo
    title = itemgetter('title')(apcEvent)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[text() = "%s"]' % (title))))
    post_btn = driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[1]/div/div[2]/div/div/div[5]/div[3]/div/div/button')
    post_btn.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Your post is now published.')]")))
    print('Post published successfully!')
    # totally not a bot
    sleep(2)

def formatDescription(apcEvent):
    title, description = itemgetter('title', 'description')(apcEvent)
    # create the event url to the apc website, essential for loading the photo
    slugifiedEventName = stringToSlug(title)
    eventURL = " https://www.apeoplescalendar.org/calendar/events/" + slugifiedEventName

    # # create image transcription message
    # imageTranscriptionMessage = ''
    # # if we have image
    # if imgAltText:
    #     imageTranscriptionMessage = '''\n\nImage Transcription: %s''' % (imgAltText)
    # else:
    #     imageTranscriptionMessage = '''\n\nImage Transcription: Looks like we don't have an image caption for this event yet. Feel free to suggest one below.''' 
    # format the comment using data from the apcEvent object
    body = '''%s\n\nRead more:\n\n%s''' % (description, eventURL)
    return body


def postEvents(eventList):
    for apcEvent in eventList:
        postEvent(apcEvent)

login()
postEvents(todayEvents)
driver.quit()
