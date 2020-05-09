
import rules

defaultStats = {
        "LARGEST_WORD_VALUE": '',
        "LONGEST_WORD": '',
        }

def getDefaultEmptyStats():
    return defaultStats


def recordStats(stats, wordList):
    longestWord = stats["LONGEST_WORD"]
    longestInWordList = max(wordList, key=len)

    if len(longestWord) < len(longestInWordList):
        stats["LONGEST_WORD"] = longestInWordList

    largestWordValue = stats["LARGEST_WORD_VALUE"]
    largestWordValueInWordList = max(wordList, key=rules.getValueOfWord)

    if rules.getValueOfWord(largestWordValue) < rules.getValueOfWord(largestWordValueInWordList):
        stats["LARGEST_WORD_VALUE"] = largestWordValueInWordList

def getLongestWord(stats):
    return stats["LONGEST_WORD"]

def getLargestWordValue(stats):
    return stats["LARGEST_WORD_VALUE"]
