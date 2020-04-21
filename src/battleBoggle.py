
#!/usr/bin/env python3

# Main program for the battle boggle game

import kivy

from kivy.app import App
from kivy.properties import NumericProperty, BooleanProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color

from kivy.logger import Logger

from random import choice

from randomletter import randomLetter
from wordsanddefinitions import isValidWord, getDefinition
from battleai import TrivialAI

from kivy.config import Config
Config.set('graphics', 'width', '1400')
Config.set('graphics', 'height', '900')
Config.set("kivy", "log_level", "info")

class BattleTile(ToggleButtonBehavior, Image):
    boggleGame = ObjectProperty(None)
    character = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.source = 'rsc/images/Wood-Tile-3.png'
        super(BattleTile, self).__init__(**kwargs)

    def on_state(self, widget, value):
        Logger.info("on_state: value: %s, character: %s", value, self.character)
        self.setSource(value)
        # Jason :: TODO: Fix this as it is called even when I'm manually setting the state.
        self.boggleGame.battleTileSelected(self)

    def setSource(self, imageState):
        if imageState == 'down':
            prefix = 'rsc/images/Wood-Tile-Selected'.format(self.character)
        else:
            prefix = 'rsc/images/Wood-Tile'.format(self.character)
        f = '{}-{}.png'.format(prefix, self.character)

        Logger.info("setSource: imageState: %s, f: %s", imageState, f)
        self.source = f

    def set_character(self, c):
        Logger.info("set_character: c: %s", c)
        self.character = c
        self.ids.l.text = c
        self.setSource('normal')

    def buttonRelease(self):
        # This happens before the state is set so therefore it is not valid to do
        # anything here that relies on the state member variable.
        pass

    def render(self):
        Logger.info("render: going to render the battle tile")
        c = Color(0.5, 0.5, 0, 1)

        self.canvas.clear()
        self.canvas.add(c)
        self.rect = Rectangle(size=self.size, pos=self.pos)
        self.canvas.add(self.rect)
        label = CoreLabel(text="{}".format(self.character), font_size=20)
        label.refresh()
        text = label.texture

        c = Color(0,0,0.5,1)
        self.canvas.add(c)
        pos = list(self.pos[i] + (self.size[i] - text.size[i]) / 2 for i in range(2))
        self.canvas.add(Rectangle(size=text.size, pos=pos, texture=text))
        self.canvas.ask_update()

class ClearArea(ButtonBehavior, GridLayout):
    pass

class BattleWord(ButtonBehavior, BoxLayout):
    wordNumber = NumericProperty(0)
    visible = BooleanProperty(True)
    boggleGame = ObjectProperty(None)

    def __init__(self,**kwargs):
        super(BattleWord, self).__init__(**kwargs)
        self.word = ''

    def get_word(self):
        return self.word
    
    def set_word(self, word):
        self.word = word
        if self.visible:
            self.ids.Word.text = word
        else:
            self.ids.Word.text = "X" * len(word)
    
    def is_word(self, word):
        return self.word == word

    def buttonRelease(self):
        self.boggleGame.showDefinition(self.word)


class BattleBoggleGame(BoxLayout):
    maxWordCount = NumericProperty(10)
    rows = NumericProperty(4)
    cols = NumericProperty(4)

    def get_cell(self, r, c):
        cellString = "R{}C{}".format(r, c)
        return self.ids[cellString]

    def init_ai(self):
        self.ai = TrivialAI()
        self.ai.set_grid(self.grid, self.rows, self.cols)
        self.ai.set_longest_word(5)
        self.ai.build()

    def init_board(self):
        
        letters = []
        self.grid = []
        for r in range(1,self.rows+1):
            row = []
            for c in range(1,self.cols+1):

                # Chose a new letter as long as we don't have too many of that letter.
                while True:
                    l = randomLetter()
                    count = len(list(filter(lambda x: x == l, letters)))
                    if count < 2:
                        break

                letters.append(l)
                self.get_cell(r, c).set_character(l)

                row.append(l)
            self.grid.append(row)

    def init_round(self):
        self.playerWords = []
        self.opponentWords = []
        self.playerWordsFound = 0
        self.opponentWordsFound = 0
        self.playerBattleWordIndex = 0
        self.opponentBattleWordIndex = 0
        self.letterSequence = []

        for x in self.playerBattleWords:
            x.set_word("")
        for y in self.opponentBattleWords:
            y.set_word("")

        self.init_board()
        self.init_ai()


    def init_game(self, t):
        self.playerBattleWords = []
        self.opponentBattleWords = []
        self.currentWord = self.ids.CurrentWord
        self.info = self.ids.Info

        for i in range(1,self.maxWordCount+1):
            w = "PlayerWord{}".format(i)
            self.playerBattleWords.append(self.ids[w])

            w = "OpponentWord{}".format(i)
            self.opponentBattleWords.append(self.ids[w])

        self.init_round()

    def battleTileSelected(self, tile):
        if tile.state == 'normal':
            i = self.letterSequence.index(tile)
            # Two cases.  Either the user clicked on the same letter and is attempting
            # to submit the word or they have clicked on another letter earlier in the word.
            Logger.info(
                    "battleTileSelected - onEnter: tile.state: %s, i: %d, len(letterSequence): %d", 
                    tile.state, i, len(self.letterSequence))
            if i == len(self.letterSequence)-1:
                self.submitWord()
            else:
                # Clicking on a letter earlier in the word removes up to that letter.
                for j in range(i, len(self.letterSequence)-1):
                    self.letterSequence[j].state = 'normal'

                self.letterSequence = self.letterSequence[:i]
                self.currentWord.text = self.currentWord.text[:i]

        elif tile.state == 'down':

            self.currentWord.text += tile.character
            self.letterSequence.append(tile)

    def removeOpponentBattleWord(self, word):
        # Look through the opponentBattleWords structure and find the first word that 
        # matches and shuffle all others upwords.
        x = 0
        while x < self.opponentBattleWordIndex:
            if self.opponentBattleWords[x].is_word(word):
                self.opponentBattleWords[x].set_word("")
                # Found the word.  Shuffle all others down.
                for y in range(x+1,self.opponentBattleWordIndex):
                    self.opponentBattleWords[y-1].set_word(self.opponentBattleWords[y].get_word())
                self.opponentBattleWords[self.opponentBattleWordIndex-1].set_word("")
                self.opponentBattleWordIndex -= 1
                return True
            x += 1
        return False

    def removePlayerBattleWord(self, word):
        # Look through the player words structure and find the word that matches and shuffle all
        # others upwords.
        x = 0
        while x < self.playerBattleWordIndex:
            if self.playerBattleWords[x].is_word(word):
                self.playerBattleWords[x].set_word("")
                # Found the word.  Shuffle all others down.
                for y in range(x+1,self.playerBattleWordIndex):
                    self.playerBattleWords[y-1].set_word(self.playerBattleWords[y].get_word())
                self.playerBattleWords[self.playerBattleWordIndex-1].set_word("")
                self.playerBattleWordIndex -= 1
                return True
        return False

    def clearCurrentWord(self):
        for l in self.letterSequence:
            l.state = 'normal'
        self.letterSequence = []
        self.currentWord.text = ''

    def add_player_word(self, word):
        # There are three cases:
        # 
        # 1/  The word was already found by the player.
        # 2/  The word was previously found by the other player
        # 3/  The word is new and added to the ones tracked.

        if word in self.playerWords:
            self.info.text = "Word '{}' already found".format(word)
        elif word in self.opponentWords:
            self.removeOpponentBattleWord(word)
            self.info.text = "Word '{}' removed from opponent".format(word)
            self.playerWords.append(word)
            self.playerWordsFound += 1
        else:
            self.info.text = "Word '{}' added".format(self.currentWord.text)
            self.playerWords.append(word)
            self.playerBattleWords[self.playerBattleWordIndex].set_word(word)
            self.playerBattleWordIndex += 1

    def add_opponent_word(self, word):
        if word in self.opponentWords:
            pass  # Doing nothing here, opponents can do this if they want
        elif word in self.playerWords:
            self.removePlayerBattleWord(word)
            self.info.text = "Word '{}' found by opponent".format(word)
            self.opponentWords.append(word)
            self.opponentWordsFound += 1
        else:
            self.opponentWords.append(word)
            self.opponentBattleWords[self.opponentBattleWordIndex].set_word(word)
            self.opponentBattleWordIndex += 1
            self.opponentWordsFound += 1
            
    def showDefinition(self, word):
        if not word == '':
            self.info.text = "{}: {}".format(word, getDefinition(word))


    def update(self, dt):
        self.ai.update(dt)
        word = self.ai.nextWord()
        if word:
            self.add_opponent_word(word)

        if self.playerBattleWordIndex == self.maxWordCount:
            self.info.text = "You won!"
            self.init_round()
        elif self.opponentBattleWordIndex == self.maxWordCount:
            self.info.text = "You lost!"
            self.init_round()


    def on_touch_up(self, touch):
        Logger.info("on_touch_up: touch: %s", touch)

    def submitWord(self):
        if isValidWord(self.currentWord.text):
            self.add_player_word(self.currentWord.text)
            self.clearCurrentWord()
        else:
            self.info.text = "'{}' is not a valid word".format(self.currentWord.text)
            self.clearCurrentWord()


class BattleBoggleApp(App):

    def build(self):
        game = BattleBoggleGame()
        Clock.schedule_once(game.init_game)
        Clock.schedule_interval(game.update,1.0/2.0)
        return game


if __name__=='__main__':
    BattleBoggleApp().run()
