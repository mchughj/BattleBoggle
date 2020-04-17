# BattleBoggle
A head-to-head and dynamic game based on the classic Boggle game

Using kivy and planning on integrating with a twister server instance.  See
example [here](https://kivy.org/doc/stable/guide/other-frameworks.html).

Kivy examples:
c:\Users\mchug\AppData\Local\Programs\Python\Python37\share\kivy-examples\tutorials\

When I get to having multiple screens use:

```
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
```
See example in 
c:\Users\mchug\AppData\Local\Programs\Python\Python37\share\kivy-examples\tutorials\notes\final\

## Features

* Basic game
** Click on letters and they stay lit up. 
** Double click on a letter to submit the word
** Click off of the grid to clear the word
** Click on a prior letter to unwind the word

* Display
** Show the words you have gotten so far
** Shadow display the words your opponent has so far.
** Show the definitions of the words when you mouse over the word

* Timed game
** Show a percentage timer
** When no word is found then the timer decreases
** Timer has a maximum time that it will wait that decreases as the game goes on
** Finding a word adds time to the timer

* AI
** Difficulty is based on length of word, time it takes to find the next word, chances of finding larger words.

* Infrastructure
** Opponent structure
** Network

* Statistics
** Longest word
** Longest time to find first word
** Longest first word
** Shortest time to find first word
** Maximum number of words in a round
** 

* Special tiles
** Any letter at all
** Use once
** Use multiple times
** Must end word (frozen)
** Must not end word
** Must begin word
** Must not begin word


* Rules
** Any letter anywhere
** Must connect
** Minimum length word



--

## Alternatives

http://pyglet.org/ - is supposed to support multiple monitors and multiple windows.  Something to consider.  The likelihood that I can get multiple touchscreen monitors working off of a single raspberry pi board though feels low.  Also this assumes always head-to-head battles playing across from one another which is a bit limiting.  (It would require a lot of space and wouldn't allow for random battles with other people.)
