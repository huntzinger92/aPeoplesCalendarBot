def getDateFromUser():
    print('input date in form MM-DD (no zero pads)')
    tempTodayString = input()
    return tempTodayString
    # trying to add a confirmation check like the below does not work, returns "None" outside of function call
    # print('you input: ' + tempTodayString + ' is that correct? (Y/n)')
    # userAnswer = input()
    # if userAnswer != 'Y':
    #     getDateFromUser()
    # else:
    #     return tempTodayString
