
from random import randint
from wordsanddefinitions import isValidWord

class TrivialAI(object):

    def __init__(self):
        self.words = list()
        self.accumulatedTime = 0
        self.nextWordFound = 0.01

    def set_grid(self, grid, r, c):
        self.grid = grid
        self.rowCount = r
        self.colCount = c

    def set_longest_word(self, l):
        self.longestWord = l

    def _build_words(self, x, y, currentWord, used):
        if x < 0 or x >= self.colCount or y < 0 or y >= self.rowCount:
            return

        if used[x][y]:
            return

        used[x][y] = True
        currentWord += self.grid[x][y]

        if len(currentWord) <= self.longestWord:
            if isValidWord(currentWord):
                self.words.append(currentWord)

            for xd in [-1,0,1]:
                for yd in [-1,0,1]:
                    self._build_words(x+xd, y+yd, currentWord, used)

        used[x][y] = False


    def build(self):
        # Trivial complete search looking for all valid words.
        # This implementation is poor as it won't work for tiles that
        # have special attributes and the AI is too simplistic.  

        # Construct a data structure 
        used = [ [ False for x in range(self.colCount) ] for y in range(self.rowCount) ]
        for x in range(self.colCount):
            for y in range(self.rowCount):
                self._build_words(x, y, "", used)

        print("build - complete; wordCount: {}, words{}".format(len(self.words), self.words))

    def update(self, dt):
        self.accumulatedTime += dt

    def nextWord(self):
        if self.accumulatedTime > self.nextWordFound:
            print("nextWord - enough time has passed; accumulatedTime: {}, numberWords: {}"
                    .format(self.accumulatedTime, len(self.words)))

            self.accumulatedTime = 0
            return self.words[ randint(0,len(self.words)-1) ]

        return None
