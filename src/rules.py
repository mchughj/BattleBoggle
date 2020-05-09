
defaultGameRules = {
        "AI_SPEED": 5,
        "AI_SMARTS": 5,
        }

def getDefaultGameRules():
    return defaultGameRules

def getSmarts(rules):
    return int(rules["AI_SMARTS"])

def getSpeed(rules):
    return int(rules["AI_SPEED"])

def getMaxWordLength(smarts):
    # smarts has an acceptable range of 0-10
    if smarts < 0:
        smarts = 0
    if smarts > 10:
        smarts = 10

    maxWordLength = int(3 + int(smarts) / 2.0)

    if maxWordLength > 8:
        maxWordLength = 8

    return maxWordLength

def getTimeRangeForNextWordDiscovery(speed):
    # Speed has an acceptable range of 0-10
    if speed < 0:
        speed = 0
    if speed > 10:
        speed = 10

    minTime = 0.5 + (5 - speed / 2)
    maxTime = 20 - speed

    return (minTime, maxTime)


letterValue = { 
        'A': 1,
        'B': 3,
        'C': 2,
        'D': 1,
        'E': 1,
        'F': 2,
        'G': 2,
        'H': 1,
        'I': 1,
        'J': 4,
        'K': 2,
        'L': 1,
        'M': 3,
        'N': 1,
        'O': 1,
        'P': 2,
        'Q': 5,
        'R': 1,
        'S': 1,
        'T': 1,
        'U': 3,
        'V': 5,
        'W': 3,
        'X': 5,
        'Y': 4,
        'Z': 5
        }

# Take a random letter that has been selected and return an alternate suggestion.
# There are three cases:
#
# 1.  The same letter is returned as the randomLetter passed in - so use that one.
# 2.  None is returned which indicates that a new random letter should be chosen.
# 3.  Another letter will be returned and that one should be used instead.
#
def confirmOrSuggestAlternateLetter(randomLetter, currentLetters): 
    # First rule - if the letter already appears multiple times then don't use it.
    count = len(list(filter(lambda x: x == randomLetter, currentLetters)))
    if count >= 2:
        return None

    # Second rule - if this will be a double and there is another double in the list of
    # letters already then don't allow an additional double.
    if count == 1:
        for f in currentLetters:
            if len(list(filter(lambda x: x == f, currentLetters))) >= 2:
                return None

    # Third rule - if the letter is a Q and no 'u' has been selected already then disallow.
    if randomLetter == 'Q':
        if len(list(filter(lambda x: x == 'U', currentLetters))) == 0:
            return None

    return randomLetter

def getValueOfWord(word):
    return sum([ getValueOfLetter(l) for l in word ] ) * len(word)

def getValueOfLetter(letter):
    return letterValue[letter]
