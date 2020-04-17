
def readDictionary(filename):
    try:
        with open(filename) as f:
            lineNumber = 0
            for line in f:
                lineNumber += 1
                try:
                    (word, partOfSpeech, definition) = line.split("\t")
                    word = word.lower()
                    # Only save the first definition
                    if not word in w:
                        w[word] = definition
                except:
                    print("Unable to parse line; number: {}, text: '{}'".format(lineNumber, line))
        return True
    except FileNotFoundException:
        return False


def isValidWord(word):
    word = word.lower()
    return word in w

def getDefinition(word):
    word = word.lower()
    return w[word]

w = {}

success = readDictionary("rsc/Dictionary/complete.txt")
if not success:
    success = readDictionary("../rsc/Dictionary/complete.txt")
