# Janggi
Adaptation of Janggi, or Korean Chess

A program for a class named JanggiGame that allows two players ("Blue" and "Red") to use the command line to play the [Janggi board game](https://en.wikipedia.org/wiki/Janggi). This version of the game does not implement the rules regarding perpetual check, position repetition, or draw logic. It does implement checkmate and all piece-specific rules, e.g. generals aren't allowed to leave the palace, horses and elephants can be blocked, cannons cannot capture other cannons, etc. 

Locations on the board are specified using "algebraic notation", with columns labeled a-i and rows labeled 1-10, with row 1 being the Red side and row 10 the Blue side. 

```
game = JanggiGame()
move_result = game.make_move('c1', 'e3') #should be False because it's not Red's turn
move_result = game.make_move('a7,'b7') #should return True
blue_in_check = game.is_in_check('blue') #should return False
game.make_move('a4', 'a5') #should return True
state = game.get_game_state() #should return UNFINISHED
game.make_move('b7','b6') #should return True
game.make_move('b3','b6') #should return False because it's an invalid move
game.make_move('a1','a4') #should return True
game.make_move('c7','d7') #should return True
game.make_move('a4','a4') #this will pass the Red's turn and return True
