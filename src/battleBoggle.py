#!/usr/bin/env python3

# Main program for the battle boggle game

import kivy

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.logger import Logger
from kivy.properties import NumericProperty, BooleanProperty, ReferenceListProperty, ObjectProperty
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.floatlayout import FloatLayout 
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.vector import Vector

from random import choice

from randomletter import randomLetter
from wordsanddefinitions import isValidWord, getDefinition
from battleai import TrivialAI
import rules
import stats

from kivy.config import Config

import configparser

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

Config.set('graphics', 'width', WINDOW_WIDTH)
Config.set('graphics', 'height', WINDOW_HEIGHT)
Config.set("kivy", "log_level", "info")

class BattleWordScore(Label):

    def animate_score(self, delay_ms):
        a = Animation(opacity=0, font_size=28, duration=0) + Animation(opacity=0, duration= (delay_ms / 1000) ) \
                + Animation(opacity=1, duration=1) + Animation(animated_color=(1,0,0,0), blink_size=90)
        a.bind(on_complete=self.reset)
        a.start(self)

    def reset(self, *args):
        self.animated_color = (1,1,1,1)
        self.blink_size = 0

        a = Animation(animated_color=(1,0,0,0), blink_size=90)
        a.bind(on_complete=self.reset)
        a.start(self)


class BattleTile(ToggleButtonBehavior, Image):
    boggleApp = ObjectProperty(None)
    character = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BattleTile, self).__init__(**kwargs)
        self.selectable = True
        self.battle_word = None

    def set_selectable(self, selectable):
        self.selectable = selectable

    def set_battle_word(self, word):
        self.battle_word = word

    def on_state(self, widget, value):
        Logger.info("on_state: value: %s, character: %s", value, self.character)
        if self.selectable:
            self.setTileImage(value)

    def setTileImage(self, imageState):
        if imageState == 'down':
            prefix = 'rsc/images/Wood-Tile-Selected'.format(self.character)
        else:
            prefix = 'rsc/images/Wood-Tile'.format(self.character)
        f = '{}-{}.png'.format(prefix, self.character)

        Logger.info("setTileImage: imageState: %s, f: %s", imageState, f)
        self.source = f

    def set_character(self, c):
        Logger.info("set_character: c: %s", c)
        self.character = c
        self.state = 'normal'
        self.setTileImage('normal')

    def _do_release(self, *args):
        if not self.selectable:
            # If it is not selectable then either it is a tile within a larger battle word
            # or it is in the grid and the game mode does not allow for selection at this time.
            if self.battle_word: 
                self.battle_word.buttonRelease()

            return 

        super(BattleTile, self)._do_release(args)
        self.boggleApp.battleTileSelected(self)


class BattleWord(ButtonBehavior, BoxLayout):
    wordNumber = NumericProperty(0)
    visible = BooleanProperty(True)
    boggleApp = ObjectProperty(None)

    def __init__(self,**kwargs):
        super(BattleWord, self).__init__(**kwargs)
        self.word = ''

    def get_word(self):
        return self.word
    
    def set_word(self, word):
        self.word = word
        if self.visible:
            self.show_word(word)
        else:
            self.show_word("X" * len(word))

    def show_current_word(self):
        self.visible = True
        self.show_word(self.word)

    def show_score(self, value, x, delay_ms):
        score = BattleWordScore(pos = (x,0))
        score.text = str(value)

        score.animate_score(delay_ms)

        with score.canvas:
            Color(1,0,0,0.5)
            Rectangle(pos = (x,0),
                    size = (40,40))

        Logger.info("show_score: adding label with value: %d", value)

        self.ids.Word.add_widget(score)

    def show_word(self, word):
        Logger.info("show_word: creating battle tiles for word: %s", word)

        self.ids.Word.clear_widgets()
        x = 10
        for (index, w) in enumerate(word):
            t = BattleTile(
                    pos=(x, 0), 
                    size=(40,40), 
                )
            t.set_battle_word(self)
            t.set_selectable(False)
            t.set_character(w)
            self.ids.Word.add_widget(t)
            x += 40
    
    def is_word(self, word):
        return self.word == word

    def buttonRelease(self):
        if self.visible:
            self.boggleApp.showDefinition(self.word)


class BattleBoggleGame(Screen, FloatLayout):
    maxWordCount = NumericProperty(10)
    rows = NumericProperty(4)
    cols = NumericProperty(4)
    playerScore = NumericProperty(0)
    opponentScore = NumericProperty(0)
    boggleApp = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BattleBoggleGame, self).__init__(**kwargs)

        self.newRoundButton = Button(text='Next Round', on_release=lambda a: self.init_round())
        self.newRoundButton.size_hint = (None, None)
        self.newRoundButton.width = 300
        self.newRoundButton.height = 100
        self.newRoundButton.pos = ((WINDOW_WIDTH - self.newRoundButton.width) / 2,100)

        self.mainMenuButton = Button(text='Return to main menu', on_release=lambda a:
                self.boggleApp.showMainMenu())
        self.mainMenuButton.size_hint = (None, None)
        self.mainMenuButton.width = 300
        self.mainMenuButton.height = 100
        self.mainMenuButton.pos = ((WINDOW_WIDTH - self.mainMenuButton.width) / 2,100)

        self.playerRoundScore = BattleWordScore(pos = (0,200))
        self.playerRoundScore.width = 70
        self.playerRoundScore.height = 70
        self.playerRoundScore.text = ''

        self.opponentRoundScore = BattleWordScore(pos = (0,200))
        self.opponentRoundScore.text = ''
        self.opponentRoundScore.width = 100
        self.opponentRoundScore.height = 100

    def set_stats(self, stats):
        self.stats = stats

    def set_game_rules(self, gameRules):
        self.gameRules = gameRules

    def get_cell(self, r, c):
        cellString = "R{}C{}".format(r, c)
        return self.ids[cellString]

    def init_ai(self):
        self.ai = TrivialAI()
        self.ai.set_grid(self.grid, self.rows, self.cols)
        self.ai.set_longest_word(rules.getMaxWordLength(self.smarts))
        self.ai.set_word_time(rules.getTimeRangeForNextWordDiscovery(self.speed))
        self.ai.build()

    def init_board(self):
        letters = []
        self.grid = []
        for r in range(1,self.rows+1):
            row = []
            for c in range(1,self.cols+1):
                l = None
                while l is None:
                    l = rules.confirmOrSuggestAlternateLetter(randomLetter(), letters)

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
        self.roundComplete = False

        for x in self.playerBattleWords:
            x.set_word("")
        for y in self.opponentBattleWords:
            y.set_word("")
            y.visible = False

        for r in range(1,self.rows+1):
            for c in range(1,self.cols+1):
                self.get_cell(r, c).set_selectable(True)

        self.init_board()
        self.init_ai()

        self.remove_widget(self.newRoundButton)
        self.remove_widget(self.mainMenuButton)
        self.remove_widget(self.playerRoundScore)
        self.remove_widget(self.opponentRoundScore)
        self.info.text = ''


    def init_game(self, t):
        self.playerBattleWords = []
        self.opponentBattleWords = []
        self.currentWord = ''
        self.currentWordDisplay = self.ids.CurrentWord
        self.info = self.ids.Info
        self.lives = 2
        self.playerScore = 0
        self.opponentScore = 0

        self.smarts = rules.getSmarts(self.gameRules)
        self.speed = rules.getSpeed(self.gameRules)

        for i in range(1,self.maxWordCount+1):
            w = "PlayerWord{}".format(i)
            try:
                self.playerBattleWords.append(self.ids[w])
            except:
                Logger.error("init_game: Unable to find ID '%s'", w)

            w = "OpponentWord{}".format(i)
            try:
                self.opponentBattleWords.append(self.ids[w])
            except:
                Logger.error("init_game: Unable to find ID '%s'", w)

        self.init_round()


    def showCurrentWord(self, word):
        Logger.info("showCurrentWord: word: %s", word)

        self.currentWordDisplay.clear_widgets()

        Logger.info("showCurrentWord: position of currentWordDisplay = %s",
                str(self.currentWordDisplay.pos))

        totalWidth = 110 * len(word) 
        x = (WINDOW_WIDTH - totalWidth) / 2
        y = self.currentWordDisplay.y + 10
        for (index, w) in enumerate(word):
            t = BattleTile(
                    pos=(x, y), 
                    size=(100,100), 
                    size_hint=(None, None))
            t.set_selectable(False)
            t.set_character(w)
            self.currentWordDisplay.add_widget(t)
            x += 110

    def battleTileSelected(self, tile):
        if tile.state == 'normal':
            Logger.info(
                    "battleTileSelected: tile info; state: %s, character: %s, letterSequence: %s",
                    tile.state, tile.character, self.currentWord)
            i = self.letterSequence.index(tile)
            # Two cases.  Either the user clicked on the same letter and is attempting
            # to submit the word or they have clicked on another letter earlier in the word.
            if i == len(self.letterSequence)-1:
                self.submitWord()
            else:
                # Clicking on a letter earlier in the word removes up to that letter.
                for j in range(i, len(self.letterSequence)):
                    self.letterSequence[j].state = 'normal'

                self.letterSequence = self.letterSequence[:i]
                self.currentWord = self.currentWord[:i]
                self.showCurrentWord(self.currentWord)

        elif tile.state == 'down':

            self.letterSequence.append(tile)
            self.currentWord += tile.character
            self.showCurrentWord(self.currentWord)

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
            x += 1
        return False

    def clearCurrentWord(self):
        for l in self.letterSequence:
            l.state = 'normal'
        self.letterSequence = []
        self.currentWord = ''
        self.showCurrentWord('')

    def add_player_word(self, word):
        # There are three cases:
        # 
        # 1/  The word was already found by the player.
        # 2/  The word was previously found by the other player
        # 3/  The word is new and added to the ones tracked.
        Logger.info("add_player_word: word: %s", word)

        if word in self.playerWords:
            self.info.text = "Word '{}' already found\n".format(word)
        elif word in self.opponentWords:
            self.removeOpponentBattleWord(word)
            self.info.text = "Word '{}' removed from opponent\n".format(word)
            self.playerWords.append(word)
            self.playerWordsFound += 1
        else:
            self.info.text = "Word '{}' added\n".format(self.currentWord)
            self.playerWords.append(word)
            self.playerBattleWords[self.playerBattleWordIndex].set_word(word)
            self.playerBattleWordIndex += 1

    def add_opponent_word(self, word):
        if word in self.opponentWords:
            pass  # Doing nothing here, opponents can do this if they want
        elif word in self.playerWords:
            self.removePlayerBattleWord(word)
            self.info.text = "Word '{}' found by opponent\n".format(word)
            self.opponentWords.append(word)
            self.opponentWordsFound += 1
        else:
            self.opponentWords.append(word)
            self.opponentBattleWords[self.opponentBattleWordIndex].set_word(word)
            self.opponentBattleWordIndex += 1
            self.opponentWordsFound += 1
            
    def showDefinition(self, word):
        if not word == '':
            Logger.info("showDefinition: word: %s, definition: %s", word, getDefinition(word))
            self.info.text = "{}: {}".format(word, getDefinition(word))


    def update(self, dt):
        if not self.roundComplete:
            self.ai.update(dt)
            word = self.ai.nextWord()
            if word:
                self.add_opponent_word(word)

            if self.playerBattleWordIndex == self.maxWordCount:
                self.info.text = "You won!\n"
                self.roundComplete = True
                self.smarts += 1
                self.speed += 1
                self.show_end_round(True)
            elif self.opponentBattleWordIndex == self.maxWordCount:
                self.info.text = "You lost!\n"
                self.roundComplete = True
                self.lives -= 1
                self.show_end_round(False)


    def score_words(self, words, multiplier, roundScoreDisplay, offsetX):
        points = 0

        # Align all of score widgets that are shown in a single vertical column.
        maxLength = max([len(x.get_word()) for x in words])
        relativePosX = 10 + 40 * maxLength + 30

        for i, x in enumerate(words):
            word = x.get_word()

            # Calculate value of the word
            value = rules.getValueOfWord(word)
            if value > 0:
                x.show_score(value, relativePosX, i * 100)
            points += value

        if multiplier:
            points *= 1.5

        roundScoreDisplay.text = str(int(points))
        roundScoreDisplay.animate_score(len(words) * 100 + 50)
        roundScoreDisplay.pos[0] = relativePosX + offsetX + 75 - roundScoreDisplay.size[0]/2.0
        self.add_widget(roundScoreDisplay)

        return int(points)


    def show_end_round(self, didPlayerWin):
        # Show all of the opponent words
        for y in self.opponentBattleWords:
            y.show_current_word()

        # Disable all of the ability to create new words.
        # Also remove the current word.
        self.clearCurrentWord()
        for r in range(1,self.rows+1):
            for c in range(1,self.cols+1):
                self.get_cell(r, c).set_selectable(False)

        # Update the stats
        stats.recordStats(self.stats, [x.get_word() for x in self.playerBattleWords])

        # Jason :: TODO:  Show the score for each word as a little glyph that animates
        # Jason :: TODO:  The animated widget could be a start or something that animates.  See https://kivy.org/doc/stable/guide/widgets.html#adding-widget-background
        # Jason :: TODO:  Show the score counting up via something like https://stackoverflow.com/questions/44955913/kivy-animation-class-to-animate-kivy-images
        
        playerRoundScore = self.score_words(self.playerBattleWords, didPlayerWin, self.playerRoundScore, self.ids.PlayerWords.pos[0] )
        self.playerScore += playerRoundScore

        opponentRoundScore = self.score_words(self.opponentBattleWords, not didPlayerWin, self.opponentRoundScore, self.ids.OpponentWords.pos[0])
        self.opponentScore += opponentRoundScore 

        if self.lives > 0:
            self.add_widget(self.newRoundButton)
        else:
            self.add_widget(self.mainMenuButton)


    def on_touch_up(self, touch):
        Logger.info("on_touch_up: touch: %s", touch)

    def submitWord(self):
        if isValidWord(self.currentWord):
            self.add_player_word(self.currentWord)
            self.clearCurrentWord()
        else:
            self.info.text = "'{}' is not a valid word\n".format(self.currentWord)
            self.clearCurrentWord()

class MenuScreen(Screen):
    pass


class BattleBoggleApp(App):
    def __init__(self, **kwargs):
        super(BattleBoggleApp, self).__init__(**kwargs)
        self.updateEvent = None
    
    def build(self):
        self.config = configparser.ConfigParser()
        if not self.config.read('config.ini'):
            Logger.info("build: config.ini file not found - using defaults")
            self.config['Records'] = stats.getDefaultEmptyStats()
            self.config['GameMode'] = rules.getDefaultGameRules()

        self.game = BattleBoggleGame(name='game')
        self.game.set_stats(self.config['Records'])
        self.game.set_game_rules(self.config['GameMode'])

        self.sm = ScreenManager()
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(self.game)

        return self.sm

    def startGame(self):
        self.sm.current = 'game'
        Clock.schedule_once(self.game.init_game)
        self.updateEvent = Clock.schedule_interval(self.game.update,1.0/2.0)

    def showMainMenu(self):
        self.writeConfig()
        self.sm.current = 'menu'
        if self.updateEvent:
            Clock.unschedule(self.updateEvent)
            self.updateEvent = None

    def battleTileSelected(self, tile):
        self.game.battleTileSelected(tile)

    def showDefinition(self, word):
        self.game.showDefinition(word)

    def writeConfig(self):
        with open('config.ini', 'w') as configFile:
            self.config.write(configFile)


if __name__=='__main__':
    BattleBoggleApp().run()
