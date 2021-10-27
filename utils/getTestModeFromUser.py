def getTestModeFromUser():
    print('test mode? (logs posts to console without posting) input Y/n')
    testMode = input()
    return testMode != 'n'