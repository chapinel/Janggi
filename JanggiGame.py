# Name: Elizabeth Chapin
# Date: 2/21/21
# Description: A program that replicates Janggi, the Korean variant of Chess. The
# program contains a class for the game itself, whose methods allow users to "play"
# a game, using the classic moves for the game. This version of the game does not
# account for ties.

import copy


class JanggiGame:
    """
    A class that creates a game object which allows two players to play the Korean chess variant, Janggi
    """
    def __init__(self):
        """
        The initialization method for the JanggiGame class. Takes no parameters, and creates three data members:
        a "players" data member that creates two Player objects to play the "game", a "board" data member that
        creates a Board object to play the game on, and a "game_state" data member that tracks whether the game
        is in progress or has been won.
        """
        self._players = {
            'blue': Player(True),
            'red': Player(False)
        }
        self._board = Board(self._players)
        self._game_state = 'UNFINISHED'

    def get_game_state(self):
        """
        :return: the current value of the "game_state" data member
        """
        return self._game_state

    def get_board(self):
        """
        :return: the current Board object associated with the Game object
        """
        return self._board

    def get_player_dictionary(self):
        """
        :return: the dictionary object that contains the two Player objects created for the game
        """
        return self._players

    def is_turn(self, player):
        """
        Method to determine whether it is the turn of the player passed as a parameter
        :param player: One of the two Player objects created for the game
        :return: Returns the value of the Player's "turn" data member - either True or False
        """
        return player.get_turn()

    def is_in_check(self, color):
        """
        Method to determine whether the player associated with the color passed is in check or not
        :param color: the color associated with a Player object - either "blue" or "red"
        :return: Returns the value of the Player's "check_status" data member - either True or False
        """
        return self.get_player_dictionary()[color].get_check_status()

    def set_board_and_players(self, board_object):
        """
        Method to set a new Board object and associate its player objects with the game's player dictionary
        :param board_object: a new Board object created using the Board class
        :return: None
        """
        self._board = board_object
        self._players = self._board.get_players()

    def set_game_state(self, player_object):
        """
        Sets the value of the Game's "game_state" data member to state that the player passed as a parameter has
        won the game (either "BLUE_WON" or "RED_WON")
        :param player_object: One of the two player objects associated with the Game class
        :return: None
        """
        self._game_state = player_object.get_color().upper() + "_WON"

    def set_board_position(self, key, value):
        """
        Associates a new value with the specified key of the current Board's tile dictionary by calling
        the Board object's "set_board_position" method
        :param key: a tile in the Board's dictionary, representing board squares - e.g., "a4"
        :param value: the new Piece object to be "placed" on that position on the board
        :return: None
        """
        self._board.set_board_position(key, value)

    def update_turn(self):
        """
        Method to switch the turn values of the game's Player objects - if a Player currently has the value of "True"
        in their "turn" data member, it will switch to "False" and vice versa
        :return: None
        """
        players = self.get_player_dictionary()
        for player in players:
            if players[player].get_turn() is False:
                players[player].set_turn(True)
            else:
                players[player].set_turn(False)

    def make_move(self, start_position, end_position):
        """
        Method that performs initial checks to see whether a desired move is valid, then passes the information
        to the "is_move_valid" method for piece-specific checks. If that method returns a True value,
        this method then calls the check_checkmate method to see whether a check or checkmate situation has been
        triggered by the move. Finally, it updates the turn and returns True. If a move is determined by this method
        or the "is_move_valid" method to be invalid, this method returns False. The turn is not updated.
        :param start_position: The starting position (on the Board) of the piece to be moved
        :param end_position: The position the player wants to move the piece to
        :return: True if the move is valid; False otherwise
        """
        # print('Attempting: ', start_position, "->", end_position)

        # set a board alias as the current tile dictionary of the associated "Board" object
        board = self.get_board().get_tiles()

        # check that the game is still in progress
        if self.get_game_state() != 'UNFINISHED':
            # print('game is already over')
            return False

        # check to make sure the given starting and ending positions are valid positions
        if start_position not in board or end_position not in board:
            # print("start or end position doesn't exist on board")
            return False

        # check that a piece exists at the given starting location
        if board[start_position] is None:
            # print('no piece exists at starting location')
            return False

        # check that it's the correct player's turn
        if board[start_position].get_player().get_turn() is False:
            # print('not your turn')
            return False

        # check that the player isn't attempting to pass the turn when they're in check
        if start_position == end_position and board[start_position].get_player().get_check_status() is True:
            # print("you can't pass turn while in check")
            return False

        # otherwise, allow them to pass the turn - don't make any changes to the board, but update the turn
        elif start_position == end_position:
            # print("you've passed the turn")
            self.update_turn()
            return True

        # determine whether the specific piece can make the move in question
        valid_and_doesnt_cause_check = self.is_move_valid(start_position, end_position)

        if valid_and_doesnt_cause_check:
            # if the piece's move ensures that their general is not or no longer in check, then the player's check
            # status should be false
            self.get_board().get_tiles()[end_position].get_player().set_check_status(False)

            # we've determined that we aren't in check - let's see whether the move CAUSES check (or checkmate)
            self.check_checkmate(end_position)

            self.update_turn()
            # print("move is valid")
            return True

        # print("move is blocked or causes check")
        return False

    def check_checkmate(self, end_position):
        """
        Method to determine whether a given move has put the other player in check or checkmate.
        :param end_position: The position that a piece has moved to on the board
        :return: none - simply updates the player's check status if check has been reached or
        updates the game state is checkmate has been reached
        """
        # creating aliases for the board's tile dictionary and the Board object itself
        board = self.get_board().get_tiles()
        current_board = self.get_board()

        # find the position of the enemy general to see if it's been placed in check
        general_position = self.find_general(board[end_position], 'enemy', board)

        friendly_pieces = self.get_friendly_or_enemy_pieces(board[end_position], 'friendly', board)

        # iterate through each friendly piece and see whether they can move to the general's position
        # on their next turn
        if self.first_check(friendly_pieces, general_position, current_board):
            # if they can capture the general, then put the other player in check
            board[general_position].get_player().set_check_status(True)
        else:
            board[general_position].get_player().set_check_status(False)

        if board[general_position].get_player().get_check_status() is True:
            # now let's look at the other player - can any of their pieces move to get the general out of check?
            friendly_pieces = self.get_friendly_or_enemy_pieces(board[general_position], 'friendly', board)
            for location in friendly_pieces:
                if str(board[location]) == 'general' or str(board[location]) == 'guard':
                    moves = self.make_general_or_guard_move(location, board)
                else:
                    moves = self.get_move_function(location, board)
                if moves is not None:
                    for move in moves:
                        # We're going to "pretend" to make a move, so we need to make a copy of the board
                        # and "hypothetically" see if the move is valid and gets the general out of check
                        hypothetical_move_board = copy.deepcopy(self.get_board())
                        piece = hypothetical_move_board.get_tiles()[location]

                        # move the piece to its hypothetical location on the copied board
                        hypothetical_move_board.set_board_position(move, piece)
                        hypothetical_move_board.set_board_position(location, None)

                        # if it's still check, reset the board and try with the next move
                        if self.still_check(move, hypothetical_move_board):
                            self.set_board_and_players(current_board)
                        # if the move breaks check, reset the board and return - no checkmate today!
                        else:
                            self.set_board_and_players(current_board)
                            # print("you can get out of check")
                            return

            # if we've iterated through every possible move for every possible piece and none of them
            # have canceled check, then it's checkmate!
            self.set_game_state(board[end_position].get_player())
            # print("checkmate")
            return

        # you can't be in checkmate if you're not in check - here we just return without any further checks
        # print("not checkmate")
        return

    def first_check(self, friendly_pieces, enemy_general_position, board):
        """
        Method that looks at the current player's pieces to see if any of them can "capture" the enemy general
        on the next turn
        :param friendly_pieces: a list of all positions containing pieces belonging to the current player
        :param enemy_general_position: the board position of the other player's general
        :param board: the current board being played on
        :return: Returns true if one of the player's pieces can capture the general next turn - i.e., has the
        other player in check. Returns false otherwise
        """
        check_board = board.get_tiles()
        # get the possible moves for each piece on the next turn
        for piece_position in friendly_pieces:
            if str(check_board[piece_position]) == 'general' or str(check_board[piece_position]) == 'guard':
                moves = self.make_general_or_guard_move(piece_position, check_board)
            else:
                moves = self.get_move_function(piece_position, check_board)

            # then see if any of those positions is the same as the enemy general's
            if moves is not None and enemy_general_position in moves:
                return True
        return False

    def still_check(self, move, board):
        """
        Method that checks to see whether a "hypothetical" move by a piece has gotten that piece's general
        out of check. To do this, it iterates through each enemy piece and sees whether they can capture
        the general on their next turn.
        :param move: The starting position of the piece being checked - this should be one of the possible
        moves determined in "check_checkmate"
        :param board: The current board being used to check positions - should be the same board that the
        piece's "hypothetical move" took place on
        :return: True if the general is still in check given the "move" position of the friendly piece. Otherwise,
        returns False
        """
        tiles = board.get_tiles()
        general_position = self.find_general(tiles[move], 'friendly', tiles)
        enemy_pieces = self.get_friendly_or_enemy_pieces(tiles[move], 'enemy', tiles)

        hypothetical_board = copy.deepcopy(board)
        if self.first_check(enemy_pieces, general_position, hypothetical_board):
            return True
        return False

    def is_move_valid(self, start_position, end_position, board=None):
        """
        Method called by the make_move method to determine whether a piece can make the move it wants to make.
        The make_move method only performs initial piece-agnostic checks, so it's the responsibility of this method
        to now determine whether the move is legal given the move logic of a piece type. Once a move has been
        determined to be valid according to the piece's logic, this method also checks to see if making the move
        would leave the piece's general open to check, which is not allowed and will be determined as an illegal move.
        :param start_position: Same start_position that was passed to make_move
        :param end_position: Same end_position that was passed to make_move
        :param board: Because this method is also used to validate "hypothetical" moves during checks for check
        or checkmate, the "board" parameter should represent the board currently being played on. By default, this
        uses the actual board associated with the Game object.
        :return: Returns true if the move is valid, otherwise returns false.
        """
        # set the board being used
        if board is None:
            hypothetical_board = copy.deepcopy(self.get_board())
        else:
            hypothetical_board = copy.deepcopy(board)

        # create an alias for our piece, once we've set the correct board
        piece = hypothetical_board.get_tiles()[start_position]

        # if the piece is a general or guard, first we check to make sure that the end position is in the palace
        if str(piece) == 'general' or str(piece) == 'guard':
            color = piece.get_player().get_color()
            if end_position not in hypothetical_board.get_palace()[color]:
                # print("piece can't move outside of palace")
                return False

            possible_moves = self.make_general_or_guard_move(start_position, hypothetical_board.get_tiles())

        else:
            possible_moves = self.get_move_function(start_position, hypothetical_board.get_tiles())

        if end_position not in possible_moves:
            # print("not a valid move for this piece")
            return False
        else:
            # "pretend" to make the move for the piece in question
            hypothetical_board.set_board_position(end_position, piece)
            hypothetical_board.set_board_position(start_position, None)

            # now find all the enemy pieces and see whether, given the move made, they can now capture
            # our general
            enemy_pieces = self.get_friendly_or_enemy_pieces(piece, 'enemy', hypothetical_board.get_tiles())

            if str(piece) == 'general':
                general_position = end_position
            else:
                general_position = self.find_general(piece, 'friendly', hypothetical_board.get_tiles())

            if self.first_check(enemy_pieces, general_position, hypothetical_board):
                # if a piece can capture the general, then this move isn't valid
                return False

            # otherwise, the move is valid, and the "pretend" board now becomes the actual board in play
            self.set_board_and_players(hypothetical_board)
            return True

    def get_move_function(self, position, board):
        """
        Method to direct the piece in question to the appropriate "make_x_move" method, to determine what
        possible moves are available given the starting position.
        :param position: The starting position of the piece in question
        :param board: The board being used to determine the possible moves - may be the actual board or a given
        "hypothetical board"
        :return: Calls the appropriate make_x_move method and returns that method's return, which is a list of
        valid end positions
        """
        if str(board[position]) == 'soldier':
            return self.make_soldier_move(position, board)
        if str(board[position]) == 'horse':
            return self.make_horse_move(position, board)
        if str(board[position]) == 'elephant':
            return self.make_elephant_move(position, board)
        if str(board[position]) == 'cannon':
            return self.make_cannon_move(position, board)
        if str(board[position]) == 'chariot':
            return self.make_chariot_move(position, board)

    def make_general_or_guard_move(self, start, board):
        """
        Because the general and guard have the same move structure, their "make_x_move" method is the same
        :param start: the starting position of the piece to generate possible moves for
        :param board: the board being used to determine the possible moves - may be the actual board or a given
        "hypothetical board"
        :return: A list of board positions that it is valid for the piece to move to, given their starting location
        """
        piece = board[start]
        # reset the piece's basic moves from their new position
        piece.set_basic_moves(start)
        # get the newly generated basic moves
        basic_moves = piece.get_basic_moves()

        on_board = [move for move in basic_moves if move in board]

        # for generals and guards, all end positions need to be in the palace
        in_palace = [move for move in on_board if move in self.get_board().get_palace()[piece.get_player().get_color()]]

        # if the end position contains a friendly piece, remove it from the list of possible moves
        not_blocked = [move for move in in_palace if board[move] is None or board[move].get_player()
                       != piece.get_player()]

        return not_blocked

    def make_soldier_move(self, start, board):
        """
        Method that uses the logic of how a soldier piece can move to generate a list of possible moves from a
        starting position for a given soldier piece.
        :param start: the starting position of the soldier
        :param board: the board being used to determine the possible moves - may be the actual board or a given
        "hypothetical board"
        :return: A list of board positions that it is valid for the piece to move to, given their starting location
        """
        piece = board[start]
        piece.set_orthogonals(start)
        piece.set_basic_moves()
        basic_moves = piece.get_basic_moves()

        # Because the soldier can move differently in the palace, we have to check to see whether it is currently
        # in the palace, at a position where it could move diagonally
        if start in self.get_board().get_palace()['diagonals']:
            piece.set_diagonals(start)
            diagonal_moves = piece.get_diagonals_in_palace()
            if piece.get_player().get_color() == 'blue':
                # soldiers can't move backwards, so it's only possible for them to end up in the opposite palace
                # not their own
                in_palace = [move for move in diagonal_moves if move in self.get_board().get_palace()['red']]
                # but we still need to make sure that they aren't moving backwards with their diagonal move
                not_backwards = [move for move in in_palace if move[1] < start[1]]
            else:
                in_palace = [move for move in diagonal_moves if move in self.get_board().get_palace()['blue']]
                not_backwards = [move for move in in_palace if move[1] > start[1]]
            basic_moves = not_backwards + basic_moves

        on_board = [move for move in basic_moves if move in board]
        not_blocked = [move for move in on_board if board[move] is None or board[move].get_player() !=
                       piece.get_player()]

        return not_blocked

    def make_cannon_move(self, start, board):
        """
        Method that uses the logic of how a cannon piece can move to generate a list of possible moves from a
        starting position for a given cannon piece.
        :param start: the starting position of the cannon
        :param board: the board being used to determine the possible moves - may be the actual board or a given
        "hypothetical board"
        :return: A list of board positions that it is valid for the piece to move to, given their starting location
        """
        piece = board[start]
        piece.set_basic_moves(start)

        # if there are no basic moves for a direction, or if there's just one (because the cannon has to hop
        # over a piece), remove that direction from the list to be checked.
        basic_moves = [sublist for sublist in piece.get_basic_moves() if sublist != [] and len(sublist) > 1]

        moves = []

        # this loop is a bit complex, but basically we're just checking to see whether, for a given direction
        # a piece contains another piece. If it does, we count that as our "hopped" piece, and each position
        # after that is a valid move for the cannon until another piece is encountered. If that piece is friendly
        # then the cannon can move UP to that position; if it's an enemy piece, the cannon can move up to and
        # INCLUDING that position
        for direction in basic_moves:
            index = 1
            hopped = 0
            while index < len(direction) and hopped <= 1:
                if board[direction[index]] is None:
                    if direction[index - 1] in moves:
                        moves.append(direction[index])
                    elif board[direction[index - 1]] is not None and str(board[direction[index - 1]]) != 'cannon':
                        moves.append(direction[index])
                        if hopped == 0:
                            hopped += 1
                elif board[direction[index]].get_player() != piece.get_player() and \
                        str(board[direction[index]]) != 'cannon':
                    if board[direction[index - 1]] is not None and str(board[direction[index - 1]]) != 'cannon':
                        if hopped == 1 or index == 1:
                            moves.append(direction[index])
                            hopped += 1
                    else:
                        if hopped == 1:
                            moves.append(direction[index])
                            hopped += 1
                        else:
                            hopped += 1
                elif board[direction[index]].get_player() == piece.get_player():
                    if board[direction[index - 1]] is not None:
                        hopped += 2
                    else:
                        hopped += 1
                index += 1

        # if the cannon is in the palace on a diagonal, then it also has the potential to move diagonally
        if start in self.get_board().get_palace()['blue'] or self.get_board().get_palace()['red']:
            if start in self.get_board().get_palace()['blue']:
                palace = self.get_board().get_palace()['blue']
            else:
                palace = self.get_board().get_palace()['red']

            diagonals = [palace[0], palace[2], palace[6], palace[8]]
            if start in diagonals:
                piece.set_palace_diagonals(start)
                in_palace = [space for space in piece.get_diagonals() if space in palace]

                # here we check to see if the first diagonal contains a non-cannon piece and if the second diagonal
                # is empty or contains an non-cannon enemy. If both conditions are met,
                # the cannon can move diagonally

                if (board[in_palace[0]] is not None and str(board[in_palace[0]]) != 'cannon') and \
                    (board[in_palace[1]] is None or board[in_palace[1]].get_player() != piece.get_player()) and \
                        str(board[in_palace[1]]) != 'cannon':
                    moves.append(in_palace[1])
        return moves

    def make_chariot_move(self, start, board):
        """
        Method that uses the logic of how a chariot piece can move to generate a list of possible moves from a
        starting position for a given chariot piece.
        :param start: the starting position of the chariot
        :param board: the board being used to determine the possible moves - may be the actual board or a given
        "hypothetical board"
        :return: A list of board positions that it is valid for the piece to move to, given their starting location
        """
        piece = board[start]
        piece.set_basic_moves(start)
        basic_moves = [sublist for sublist in piece.get_basic_moves() if sublist != []]
        not_blocked = []

        # here, we loop through each direction to see how far the cannon can move until it hits another piece.
        # All of the empty spaces are counted as moves, and, if the piece is an enemy, that space is also counted.
        for direction in basic_moves:
            index = 0
            while index < len(direction):
                if board[direction[index]] is None:
                    if index == len(direction) - 1:
                        not_blocked += direction
                    index += 1
                elif board[direction[index]].get_player() != piece.get_player():
                    if index != len(direction) - 1:
                        not_blocked += direction[0:index + 1]
                        break
                    else:
                        not_blocked += direction
                        break
                else:
                    not_blocked += direction[0:index]
                    break

        # if the chariot is in the palace, it can move diagonally along the diagonal lines.
        if start in self.get_board().get_palace()['blue'] or self.get_board().get_palace()['red']:
            if start in self.get_board().get_palace()['blue']:
                palace = self.get_board().get_palace()['blue']
            else:
                palace = self.get_board().get_palace()['red']

            if start in [palace[0], palace[2], palace[4], palace[6], palace[8]]:
                piece.set_palace_diagonals(start)
                diagonals = piece.get_diagonals()
                in_palace = [space for space in diagonals if space in palace]

                # here we check to see if the first diagonal is valid, and, if it is, whether the second diagonal
                # is valid or not.
                index = 0
                while index < len(in_palace):
                    if board[in_palace[index]] is not None:
                        if board[in_palace[index]].get_player() != piece.get_player() and index != len(in_palace) - 1:
                            del in_palace[index + 1]
                            index += 1
                        elif board[in_palace[index]].get_player() == piece.get_player():
                            del in_palace[index]
                            index += 1
                    index += 1

                not_blocked += in_palace
        return not_blocked

    def make_mammal_move(self, start, board):
        """
        This method is used as a starting place for the elephant and the horse move sets. Since both pieces can
        be blocked by another piece being in their starting orthogonal move, this method checks each orthogonal
        direction from an elephant's or horse's starting position and removes that direction if it finds it blocked.
        :param start: the starting position of the horse or elephant
        :param board: the board being used to determine the possible moves - may be the actual board or a given
        "hypothetical board"
        :return: The list of directions for the piece to move, with any directions blocked orthogonally removed
        """
        piece = board[start]
        if str(piece) == 'horse':
            piece.set_basic_moves(1)
        else:
            piece.set_elephant_moves()

        basic_moves = [direction for direction in piece.get_basic_moves() if direction[0] in board]
        not_blocked = []

        for direction in basic_moves:
            if board[direction[0]] is None:
                not_blocked.append(direction)

        return not_blocked

    def make_horse_move(self, start, board):
        """
        Method that uses the logic of how a horse piece can move to generate a list of possible moves from a
        starting position for a given horse piece.
        :param start: the starting position of the horse
        :param board: the board being used to determine the possible moves - may be the actual board or a given
        "hypothetical board"
        :return: A list of board positions that it is valid for the piece to move to, given their starting location
        """
        not_blocked_first = self.make_mammal_move(start, board)

        only_diagonals = []

        # here we strip the orthogonal space and create a list of only the diagonal moves (end positions)
        for direction in not_blocked_first:
            for item in direction[1]:
                only_diagonals.append(item)

        # for each diagonal, we make sure that it's on the board and it's not blocked by a friendly piece
        for space in only_diagonals:
            if space not in board:
                only_diagonals.remove(space)
            elif board[space] is not None and board[space].get_player() == board[start].get_player():
                only_diagonals.remove(space)

        return only_diagonals

    def make_elephant_move(self, start, board):
        """
        Method that uses the logic of how an elephant piece can move to generate a list of possible moves from a
        starting position for a given elephant piece.
        :param start: the starting position of an elephant
        :param board: the board being used to determine the possible moves - may be the actual board or a given
        "hypothetical board"
        :return: A list of board positions that it is valid for the piece to move to, given their starting location
        """
        not_blocked_first = self.make_mammal_move(start, board)
        only_diagonals = []
        final_moves = []

        # here we strip the orthogonal space and create a list of only the diagonal moves (end positions)
        for direction in not_blocked_first:
            only_diagonals.append(direction[1])
            only_diagonals.append(direction[2])

        # for each diagonal, we make sure that it's on the board and it's empty (not blocked)
        for diagonal in only_diagonals:
            first_diagonal = diagonal[0] in board
            second_diagonal = diagonal[1] in board

            if first_diagonal and second_diagonal:
                if board[diagonal[0]] is None:
                    final_moves.append(diagonal)

        # for the final diagonal, we make sure that it's either empty or contains an enemy piece
        final_moves = [item[1] for item in final_moves if board[item[1]] is None or
                       board[item[1]].get_player() != board[start].get_player()]

        return final_moves

    def find_general(self, piece, friendly_or_enemy, board):
        """
        Method to locate the friendly or enemy general when determining check or checkmate
        :param piece: the piece to use to find the general
        :param friendly_or_enemy: whether we should look for the general OF the given piece, or the ENEMY general
        of the given piece
        :param board: the board being used to determine the possible moves - may be the actual board or a given
        "hypothetical board"
        :return: The single board tile that the general is on, e.g., "e2"
        """
        for tile in board:
            if friendly_or_enemy == 'friendly':
                if str(board[tile]) == 'general' and board[tile].get_player() == piece.get_player():
                    return tile
            else:
                if str(board[tile]) == 'general' and board[tile].get_player() != piece.get_player():
                    return tile

    def get_friendly_or_enemy_pieces(self, piece_in_question, friendly_or_enemy, board):
        """
        Method to generate a list of the positions of all pieces friendly to or enemies of the given starting
        piece. This is used during check/checkmate to run through all friendly/enemy pieces and see whether they
        can capture a given general.
        :param piece_in_question: the piece to use a starting place (to either find pieces friendly to it or its
        enemies)
        :param friendly_or_enemy: signifies whether you want to find pieces friendly to the starting piece, or
        that piece's enemies
        :param board: the board being used to determine the possible moves - may be the actual board or a given
        "hypothetical board"
        :return: A list of board tiles where friendly/enemy pieces were found
        """

        friendly_or_enemy_pieces = []

        for tile in board:
            if board[tile] is not None:
                enemy = board[tile].get_player() != piece_in_question.get_player()
                friendly = board[tile].get_player() == piece_in_question.get_player()

                if friendly_or_enemy == 'friendly':
                    if friendly:
                        friendly_or_enemy_pieces.append(tile)

                else:
                    if enemy:
                        friendly_or_enemy_pieces.append(tile)

        return friendly_or_enemy_pieces


class Player:
    """
    A class that creates Player objects to associate with the Game class and various Piece classes. Each
    Piece object is tied to a Player object, so that it's possible to distinguish between which "side" a piece
    is on. In this program, Player objects are initially created by the Game object, then passed to the Board object
    (also created by the Game object), which, in turn, ties the Player object to a created Piece object.
    """
    def __init__(self, turn):
        """
        Initialization method for the Player class. When the Players are created for the first time, blue is given
        the first turn, so if "turn" boolean is True, then the piece's color is "Blue". Also initializes a "check"
        data member, to keep track of which player is in check at any given time.
        :param turn: Boolean value that represents the starting turn - if True, it means this player will start the
        game; if false, it means this player will go second.
        """
        self._in_check = False
        self._turn = turn
        if turn is False:
            self._color = 'red'
        else:
            self._color = 'blue'

    def get_check_status(self):
        """
        Returns the current value (boolean) of the player's "in_check" data member
        """
        return self._in_check

    def get_turn(self):
        """
        Returns the current value (boolean) of the player's "boolean" data member
        """
        return self._turn

    def get_color(self):
        """
        Returns the current value (boolean) of the player's "color" data member
        """
        return self._color

    def set_turn(self, boolean):
        """
        Method to set the "turn" for the player
        :param boolean: either True or False
        :return: None
        """
        self._turn = boolean

    def set_check_status(self, boolean):
        """
        Method to set whether or not a Player is in "check"; updates their "in_check" data member
        :param boolean: either True, if the player is in check, or False, if the player is not in check
        :return: None
        """
        self._in_check = boolean


class Board:
    """
    The "Board" class is responsible for keeping track of the location of each piece, and for governing the limits
    of the board's "palace". It is created by a particular instance of the Game class and, in turn, creates each
    Piece object that will be used in the game. The Game object will repeatedly ask the Board for information regarding
    where different pieces are located on the board and whether or not a particular piece is inside or outside of the
    board's "palace" zone. The Game object will also use the Board to find the locations of all pieces currently
    causing a "check" condition in the game.

    Because the Board creates the necessary Piece objects for a particular game, it must also have knowledge of the
    Player objects created for that game. The Game object will pass these objects to the Board object on creation, and
    the Board object will, in turn, pass the appropriate Player object to the Piece being created. This is so that Piece
    objects have knowledge of turn and check mechanics.
    """
    def __init__(self, player_dictionary):
        """
        Initializes the Board object to be used alongside the Game object that created it. Initializes a "players"
        dictionary that is the same as the Game's player dictionary, to be used to pass Player objects to each Piece
        object. Also initializes a "palace" attribute that defines which tiles on the board qualify as the "palace",
        and a "tiles" attribute. The "tiles" attribute is a dictionary that contains the board tiles as keys
        and creates Piece objects as the key's value. If no piece is currently associated with a tile,
        that key's value is None.
        :param player_dictionary: the dictionary created as the associated Game object's "players" attribute; used
        to initialize the same value in the Board class so that Piece objects have access to the same Player objects
        as the Game
        """
        self._players = player_dictionary
        self._palace = {
            'red': ['d1', 'd2', 'd3', 'e1', 'e2', 'e3', 'f1', 'f2', 'f3'],
            'blue': ['d10', 'd9', 'd8', 'e10', 'e9', 'e8', 'f10', 'f9', 'f8'],
            'diagonals': ['d1', 'f1', 'e2', 'd3', 'f3', 'd8', 'f8', 'e9', 'd10', 'f10']
        }
        self._tiles = {
            'd8': None,
            'd9': None,
            'd10': Guard('d10', self._players['blue']),
            'e8': None,
            'e9': General('e9', self._players['blue']),
            'e10': None,
            'f8': None,
            'f9': None,
            'f10': Guard('f10', self._players['blue']),
            'd1': Guard('d1', self._players['red']),
            'd2': None,
            'd3': None,
            'e1': None,
            'e2': General('e2', self._players['red']),
            'e3': None,
            'f1': Guard('f1', self._players['red']),
            'f2': None,
            'f3': None,
            'a1': Chariot('a1', self._players['red']),
            'a2': None,
            'a3': None,
            'a4': Soldier('a4', self._players['red']),
            'a5': None,
            'a6': None,
            'a7': Soldier('a7', self._players['blue']),
            'a8': None,
            'a9': None,
            'a10': Chariot('a10', self._players['blue']),
            'b1': Elephant('b1', self._players['red']),
            'b2': None,
            'b3': Cannon('b3', self._players['red']),
            'b4': None,
            'b5': None,
            'b6': None,
            'b7': None,
            'b8': Cannon('b8', self._players['blue']),
            'b9': None,
            'b10': Elephant('b10', self._players['blue']),
            'c1': Horse('c1', self._players['red']),
            'c2': None,
            'c3': None,
            'c4': Soldier('c4', self._players['red']),
            'c5': None,
            'c6': None,
            'c7': Soldier('c7', self._players['blue']),
            'c8': None,
            'c9': None,
            'c10': Horse('c10', self._players['blue']),
            'd4': None,
            'd5': None,
            'd6': None,
            'd7': None,
            'e4': Soldier('e4', self._players['red']),
            'e5': None,
            'e6': None,
            'e7': Soldier('e3', self._players['blue']),
            'f4': None,
            'f5': None,
            'f6': None,
            'f7': None,
            'g1': Elephant('g1', self._players['red']),
            'g2': None,
            'g3': None,
            'g4': Soldier('g4', self._players['red']),
            'g5': None,
            'g6': None,
            'g7': Soldier('g7', self._players['blue']),
            'g8': None,
            'g9': None,
            'g10': Elephant('g10', self._players['blue']),
            'h1': Horse('h1', self._players['red']),
            'h2': None,
            'h3': Cannon('h3', self._players['red']),
            'h4': None,
            'h5': None,
            'h6': None,
            'h7': None,
            'h8': Cannon('h8', self._players['blue']),
            'h9': None,
            'h10': Horse('h10', self._players['blue']),
            'i1': Chariot('i1', self._players['red']),
            'i2': None,
            'i3': None,
            'i4': Soldier('i4', self._players['red']),
            'i5': None,
            'i6': None,
            'i7': Soldier('i7', self._players['blue']),
            'i8': None,
            'i9': None,
            'i10': Chariot('i10', self._players['blue']),

        }

    def get_tiles(self):
        """
        Returns the dictionary associated with the Board's "tiles" attribute.
        """
        return self._tiles

    def get_palace(self):
        """
        Returns the list of tiles that define the palace. Used by the Game class to determine whether a Piece
        is currently in or out of the palace, because that determines some pieces' movement logic.
        """
        return self._palace

    def get_players(self):
        """
        Returns the player dictionary that contains both "Player" objects currently associated with the board
        """
        return self._players

    def set_board_position(self, new, piece_or_none):
        """
        Sets a new value at the given tile. Once a piece moves, the Game object will call this method twice - once to
        associate the piece to its new tile (i.e., dictionary key), thereby also "capturing" any piece at that location
        by removing it from the dictionary, and once to clear the piece's old location by associating "None" to that
        tile.
        :param new: The key that should be given a new association - must be a tile on the board
        :param piece_or_none: Either the Piece object that should be associated with the given tile, or "None", which
        means that the tile is now empty
        :return: None
        """
        self._tiles[new] = piece_or_none
        if piece_or_none is not None:
            piece_or_none.set_orthogonals(new)


class Piece:
    """
    The parent "Piece" class is responsible for determining the starting movement logic of a piece, given
    no restraints - i.e., if a board or other pieces didn't exist, which general directions could a piece move in?

    The parent class contains attributes general to all of the child classes: the player
    to which the piece belongs, and the basic orthogonal moves of that piece given the current value of its position
    attribute.

    It also contains a method for determining basic diagonals, which is used in different ways by separate piece
    types.

    Piece objects are created by the Board object (created, in turn, by the Game object), with knowledge of their
    position on the board's tiles and knowledge of which Player object they are bound to. The Game object communicates
    with Piece objects through the intermediary of the Board object to determine move, check/checkmate, and player
    mechanics.
    """
    def __init__(self, position, player):
        """
        Initialization method for the Piece class - sets the Piece's "player" value, "basic_moves"
        value, and four orthogonal values - "left", "right", "up", "down". These are separate attributes from the
        "basic_moves" value, because the subclasses of Piece use these orthogonal directions in their own methods
        in varying ways (for example, using left to calculate a diagonal from that position).
        :param position: the starting tile of the Piece - should be a tile on the Board
        :param player: the Player object that the piece should be associated to
        """
        self._player = player
        self._basic_moves = []

        self._left_move = chr(ord(position[0]) - 1) + position[1:]
        self._right_move = chr(ord(position[0]) + 1) + position[1:]
        self._down_move = position[0] + str(int(position[1:]) - 1)
        self._up_move = position[0] + str(int(position[1:]) + 1)

    def get_basic_moves(self):
        """
        Returns the list of basic moves (set based on the current position of the piece). These are "basic" moves
        in the sense that they don't take into consideration the board or other pieces, only the piece's movement
        logic.
        """
        return self._basic_moves

    def get_player(self):
        """
        Returns the Player object associated with the piece
        """
        return self._player

    def set_orthogonals(self, position):
        """
        Whenever the piece gets a new position, the orthogonal direction values are reset
        using that new position as the base, so that Game is always getting the most up-to-date information on
        where a piece can move.
        :param position: the new_position associated to the Piece (the new tile on the board)
        :return: None
        """
        self._left_move = chr(ord(position[0]) - 1) + position[1:]
        self._right_move = chr(ord(position[0]) + 1) + position[1:]
        self._down_move = position[0] + str(int(position[1:]) - 1)
        self._up_move = position[0] + str(int(position[1:]) + 1)

    def diagonals(self, position, spaces):
        """
        Method that finds and returns the diagonal positions that a piece can move given the provided position -
        finds the up-left, up-right, down-left, and down-right diagonals the number of spaces away from the starting
        position as determined by the "spaces" parameter.

        This method is used by a number of subclasses as a starting point for determining a piece's possible moves
        in a given direction or in special circumstances. For example, the Soldier class uses this to find the
        up-left and up-right diagonals it can move to while in the palace.
        :param position: current position of the piece
        :param spaces: the number of tiles to move diagonally
        :return: a list of the 4 diagonal spaces from the provided position
        """
        if self._player.get_color() == 'blue':
            up_left_diagonal = chr(ord(position[0]) - spaces) + str(int(position[1:]) + spaces)
            down_left_diagonal = chr(ord(position[0]) - spaces) + str(int(position[1:]) - spaces)
            up_right_diagonal = chr(ord(position[0]) + spaces) + str(int(position[1:]) + spaces)
            down_right_diagonal = chr(ord(position[0]) + spaces) + str(int(position[1:]) - spaces)
        else:
            up_left_diagonal = chr(ord(position[0]) - spaces) + str(int(position[1:]) - spaces)
            down_left_diagonal = chr(ord(position[0]) - spaces) + str(int(position[1:]) + spaces)
            up_right_diagonal = chr(ord(position[0]) + spaces) + str(int(position[1:]) - spaces)
            down_right_diagonal = chr(ord(position[0]) + spaces) + str(int(position[1:]) + spaces)

        diagonals = [up_left_diagonal, down_left_diagonal, up_right_diagonal, down_right_diagonal]
        return diagonals


class Soldier(Piece):
    """
    A child class that breaks out specific movement logic for Soldier pieces. Using the orthogonal spaces generated
    by the parent Piece class, the Soldier class then determines which of those movements the Soldier is allowed to
    take - again, given no board restraints and with no knowledge of other pieces.

    It also defines diagonal movement for the Solider piece, which is used only in specific scenarios. The Game object
    determines when different types of movement should be used by a Soldier piece, based on the Board state, and asks
    for the appropriate type.
    """
    def __init__(self, position, player):
        """
        Inherits from the Piece init method (uses super()), but also defines its own "diagonals" attribute for use
        when determining palace movement. The init method also calls the "set_basic_moves" method for the solider,
        so that the starting basic moves for the soldier align with its piece logic.
        :param position: the tile that the piece starts on - should be a key in the board dictionary
        :param player: the Player object that the piece should be associated to
        """
        super().__init__(position, player)
        self._diagonals = []
        self.set_basic_moves()
        self.set_diagonals(position)

    def __str__(self):
        """
        An override of the str dunder method for use in the Game class when determining what type of piece is
        being handled
        :return: Returns the string 'soldier'
        """
        return 'soldier'

    def get_diagonals_in_palace(self):
        """
        Returns the list of diagonal moves (the "diagonal" attribute) for use in determining what possible moves
        a soldier has when it's in the palace
        """
        return self._diagonals

    def set_basic_moves(self):
        """
        Method to determine the possible orthogonal moves for this piece type - this does not account for other pieces
        on the board or even the board limits. It is only meant as a starting place of "possible moves" that the
        Game class will further define at move time.
        :return: None
        """
        if self._player.get_color() == 'blue':
            self._basic_moves = [self._left_move, self._right_move, self._down_move]
        else:
            self._basic_moves = [self._left_move, self._right_move, self._up_move]

    def set_diagonals(self, position):
        """
        Method to set possible diagonal moves for this piece type - uses the "diagonals" method of the Piece class
        for its foundation and removes the "down" diagonal (what "down" is depends on piece color).
        :return: None
        """
        if self._player.get_color() == 'blue':
            diagonals = self.diagonals(position, 1)
            self._diagonals = diagonals[0:-1:2]


class Rolling(Piece):
    """
    The Rolling child class is used to contain movement logic common to both Cannon pieces and Chariot pieces,
    which are children of the Rolling class.

    Because Cannons and Chariots are governed by the same general movement rules, not taking the position of other
    pieces into account, there is no need to define their movement logic separately. However, when other pieces are
    in play, they do operate slightly differently, which means that the Game object needs to be able to distinguish
    between the two during gameplay.

    The Rolling class is never called/used directly - its only function is to hold logic used by both the Cannon and
    Chariot classes.
    """
    def __init__(self, position, player):
        """
        Inherits from the Piece init method (uses super()), but also defines its own "diagonals" attribute for use
        when determining palace movement. The init method also calls the "set_basic_moves" method for the rolling
        piece types, so that the starting basic moves for the cannon and chariot align with their piece logic.
        :param position: the tile that the piece starts on - should be a key in the board dictionary
        :param player: the Player object that the piece should be associated to
        """
        super().__init__(position, player)
        self.set_basic_moves(position)
        self._diagonals = []

    def get_diagonals(self):
        """
        Returns the current possible diagonal moves for use in determining where the cannon or chariot can move
        when inside the palace.
        """
        return self._diagonals

    def set_basic_moves(self, position):
        """
        Method to determine the possible orthogonal moves for these piece types - this does not account for other pieces
        on the board, but does take into account board limits. It is only meant as a starting place of "possible moves"
        that the Game class will further define at move time.

        Calls, in turn, each of the methods below to set each of the directions with the list of board spaces the
        methods return. This means that the "basic_moves" for this class end up in the format:
        [[up_moves],[left_moves],[right_moves],[down_moves]].
        :return: None
        """
        up_moves = self.moving_up_or_down(position, -1)
        down_moves = self.moving_up_or_down(position, 1)
        left_moves = self.moving_left_or_right(position, -1)
        right_moves = self.moving_left_or_right(position, 1)

        basic_moves = [up_moves, down_moves, left_moves, right_moves]

        self._basic_moves = basic_moves

    def moving_up_or_down(self, position, delta, up_or_down_moves=None):
        """
        Recursive method that calls itself to keep determining the next position on the board until the board
        limits are reached. This is the only piece class that actually takes board limits into account, since some
        base case was necessary for the recursion.

        The recursion subtracts or adds (based on the delta passed, which will be +1 or -1) from the position passed
        on each call. This means that the method ends up returning a list of positions in up or down in a column - e.g.:
        ['a4', 'a3', 'a2', 'a1']
        :param position: the starting position of the piece
        :param delta: the change to make on each call - either add 1 (1) or subtract 1 (-1) from the current position
        :param up_or_down_moves: the list of moves that gets added to each pass; default is none to avoid mutation
        :return: the final list of "up_or_down_moves" once the board limits are reached in the intended direction
        """
        if up_or_down_moves is None:
            up_or_down_moves = []
        if 10 < int(position[1:]) or int(position[1:]) < 1:
            return up_or_down_moves[:-1]
        one_up_or_down = position[0] + str(int(position[1:]) + delta)
        up_or_down_moves.append(one_up_or_down)
        return self.moving_up_or_down(one_up_or_down, delta, up_or_down_moves)

    def moving_left_or_right(self, position, delta, left_or_right_moves=None):
        """
        Same as above method except for left or right - so, instead of subtracting from / adding to the column on each
        pass, it subtracts from / adds to the row and returns a list of row positions. E.g.: ['f4', 'g4', 'h4', 'i4']
        :param position: the starting position of the piece
        :param delta: the change to make on each call - either add 1 (1) or subtract 1 (-1) from the current position
        :param left_or_right_moves:
        :return: the final list of "up_or_down_moves" once the board limits are reached in the intended direction
        """
        if left_or_right_moves is None:
            left_or_right_moves = []
        if 'i' < position[0] or position[0] < 'a':
            return left_or_right_moves[:-1]
        one_left_or_right = chr(ord(position[0]) + delta) + position[1:]
        left_or_right_moves.append(one_left_or_right)
        return self.moving_left_or_right(one_left_or_right, delta, left_or_right_moves)

    def set_palace_diagonals(self, position):
        """
        Calls the Piece class' diagonal method twice - once to get the adjacent diagonal to the current position
        and once to get the diagonal adjacent to the first diagonal. Both diagonals are necessary for different
        reasons and will both be needed by the Game class to determine whether a piece can move in the palace (more
        detailed explain in the Game class methods for movement)

        Sets the class' "diagonals" value to the end result of this method.
        :param position: the starting position of the piece
        :return: None
        """
        up_left_diagonals = []
        up_right_diagonals = []
        down_left_diagonals = []
        down_right_diagonals = []

        for index in range(1, 3):
            diagonals = self.diagonals(position, index)
            up_left_diagonals.append(diagonals[0])
            up_right_diagonals.append(diagonals[2])
            down_left_diagonals.append(diagonals[1])
            down_right_diagonals.append(diagonals[3])

        self._diagonals = up_left_diagonals + up_right_diagonals + down_left_diagonals + down_right_diagonals


class Chariot(Rolling):
    """
    A child of the Rolling class. Contains no unique logic, but is differentiated from the Cannon class so that the
    Game object knows how to handle its specific interactions with other pieces on the board. It is created by the
    Board class at the start of a game instance.
    """
    def __init__(self, position, player):
        """
        Same as Rolling initialization - simply inherits from it using super() (i.e., no special logic)
        :param position: the tile that the piece starts on - should be a key in the board dictionary
        :param player: the Player object that the piece should be associated to
        """
        super().__init__(position, player)

    def __str__(self):
        """
        An override of the str dunder method for use in the Game class when determining what type of piece is
        being handled
        :return: Returns the string 'cannon'
        """
        return 'chariot'


class Cannon(Rolling):
    """
    A child of the Rolling class. Contains no unique logic, but is differentiated from the Chariot class so that the
    Game object knows how to handle its specific interactions with other pieces on the board. It is created by the
    Board class at the start of a game instance.
    """
    def __init__(self, position, player):
        """
        Same as Rolling initialization - simply inherits from it using super() (i.e., no special logic)
        :param position: the tile that the piece starts on - should be a key in the board dictionary
        :param player: the Player object that the piece should be associated to
        """
        super().__init__(position, player)

    def __str__(self):
        """
        An override of the str dunder method for use in the Game class when determining what type of piece is
        being handled
        :return: Returns the string 'cannon'
        """
        return 'cannon'


class Mammal(Piece):
    """
    The Mammal child class is used to contain movement logic common to both Elephant and Horse pieces, which are
    children of the Mammal class.

    Elephants and Horses are governed by the same movement logic, with slight differences, so the Mammal class
    creates the foundation off of which both pieces' possible moves are generated.

    The Mammal class is never called/used directly - its only function is to hold logic used by both the Elephant
    and Horse classes.
    """

    def __init__(self, position, player):
        """
        Same as Piece initialization - simply inherits from it using super() (i.e., no special logic)
        :param position: the tile that the piece starts on - should be a key in the board dictionary
        :param player: the Player object that the piece should be associated to
        """
        super().__init__(position, player)

    def set_basic_moves(self, spaces):
        """
        Method to set the basic moves for each mammal class. Uses the base orthogonal moves from the Piece class
        to first determine the orthogonal moves from the starting position. Then it calls the "mammal_diagonals"
        method below to determine the diagonal moves from each of those orthogonal moves. The spaces parameter
        passed to the mammal_diagonals method to determine how far diagonally to move - e.g., passing 2 would
        find a position two spaces diagonally from the starting position.

        Ends up setting the basic moves in the form [[orthogonal move[diagonal, diagonal], [orthogonal...etc.]]
        :param spaces: the number of spaces the piece can move diagonally (after moving orthogonally)
        :return: None
        """
        self._basic_moves = self.mammal_diagonals(spaces)

    def mammal_diagonals(self, spaces):
        """
        Uses the Piece class' base diagonal method to determine the two diagonal moves from each orthogonal
        position. For example, if the piece starts at 'b4', then this method would determine that the two
        diagonal positions to the right would be 'd3' and 'd5' (the piece moves right to 'c4' and then can
        move up to the right or down to the right).

        Uses the spaces parameter to determine the number of diagonal spaces to move. To use the same example,
        passing "1" would return 'd3' and 'd5', but passing "2" would return 'e2' and 'e6'. This allows this
        method to be used for both the horse and the elephant (since they move in the same manner, with the
        only difference being the number of diagonals).
        :param spaces: the number of spaces the piece can move diagonally (after moving orthogonally)
        :return: Returns the a list of lists (two diagonal spaces comprise a list, with four lists, one for
        each direction)
        """
        left_diagonals = self.diagonals(self._left_move, spaces)
        left_move = [left_diagonals[0], left_diagonals[1]]
        right_diagonals = self.diagonals(self._right_move, spaces)
        right_move = [right_diagonals[2], right_diagonals[3]]
        if self._player.get_color() == 'blue':
            up_once = self._down_move
            down_once = self._up_move
            up_diagonals = self.diagonals(self._down_move, spaces)
            down_diagonals = self.diagonals(self._up_move, spaces)
        else:
            up_once = self._up_move
            down_once = self._down_move
            up_diagonals = self.diagonals(self._up_move, spaces)
            down_diagonals = self.diagonals(self._down_move, spaces)
        up_move = [up_diagonals[1], up_diagonals[3]]
        down_move = [down_diagonals[0], down_diagonals[2]]
        return [[self._left_move, left_move], [self._right_move, right_move], [up_once, up_move],
                [down_once, down_move]]


class Horse(Mammal):
    """
    A child of the Mammal class. Uses the base logic in the Mammal class to generate its possible moves. It is
    created by the Board class at the start of a game instance.
    """
    def __init__(self, position, player):
        """
        Same as Mammal initialization - except that it also sets the starting Horse moves by passing "1"
        as the number of diagonal spaces to move to the Mammal class' "set_basic_moves" method
        :param position: the tile that the piece starts on - should be a key in the board dictionary
        :param player: the Player object that the piece should be associated to
        """
        super().__init__(position, player)
        self.set_basic_moves(1)

    def __str__(self):
        """
        An override of the str dunder method for use in the Game class when determining what type of piece is
        being handled
        :return: Returns the string 'horse'
        """
        return 'horse'


class Elephant(Mammal):
    """
    A child of the Mammal class. Uses the base logic in the Mammal class to generate its possible moves. It is
    created by the Board class at the start of a game instance.
    """
    def __init__(self, position, player):
        """
        Same as Mammal initialization - except that it also sets the starting Elephant moves by calling its own
        special method.
        :param position: the tile that the piece starts on - should be a key in the board dictionary
        :param player: the Player object that the piece should be associated to
        """
        super().__init__(position, player)
        self.set_elephant_moves()

    def __str__(self):
        """
        An override of the str dunder method for use in the Game class when determining what type of piece is
        being handled
        :return: Returns the string 'elephant'
        """
        return 'elephant'

    def set_elephant_moves(self):
        """
        This method essentially calls the "set_basic_moves" method of the Mammal class twice - once passing "1"
        as the number of diagonal spaces and once passing "2" as the number.

        This is to allow a slight modification of the final form of the basic moves list. Instead of [[orthogonal,
        [diagonal, diagonal], [orthogonal, [diagonal, diagonal]], etc....], it returns a list in the form:

        [[orthogonal, [[diagonal 1, diagonal 2], [diagonal 1, diagonal 2]], orthogonal....etc.]. This allows
        the Game class to easily check for blockers at each step of the Elephant's path.
        :return: None (sets the value directly, doesn't return)
        """
        first = self.mammal_diagonals(1)
        second = self.mammal_diagonals(2)

        basic_moves = []

        for item in first:
            basic_moves.append([item[0]])

        for index in range(len(first)):
            basic_moves[index].append([first[index][1][0]])
            basic_moves[index].append([first[index][1][1]])

        for index in range(len(second)):
            basic_moves[index][1].append(second[index][1][0])
            basic_moves[index][2].append(second[index][1][1])

        self._basic_moves = basic_moves


class Palace(Piece):
    """
    The Palace child class is used to contain movement logic that is common to both the General and Guard classes,
    which are children of the Palace class.

    Both Generals and Guards move in the same way and so there is no need to declare the same movement logic
    twice. However, having each class broken out allows the Game object to differentiate between these pieces
    for game mechanics involving check and checkmate.

    The Palace class is never called/used directly - its only function is to hold logic used by both the General
    and Guard classes.
    """
    def __init__(self, position, player):
        """
        Inherits from the Piece init method (uses super()), but calls its own "set_basic_moves" method,
        so that the starting basic moves for the General and Guard align with their piece logic.
        :param position: the tile that the piece starts on - should be a key in the board dictionary
        :param player: the Player object that the piece should be associated to
        """
        super().__init__(position, player)
        self.set_basic_moves(position)

    def set_basic_moves(self, position):
        """
        Uses the basic orthogonal and diagonal moves defined in the Piece class to set the list of possible
        moves for the General and Guard classes. Again, these are only meant as a starting place and will be
        further refined by the Game class during move time.
        :return: None
        """
        diagonal_points = ['d10', 'd8', 'e9', 'f8', 'f10', 'd1', 'd3', 'e2', 'f1', 'f3']
        if self._player.get_color() == 'blue':
            self._basic_moves = [self._left_move, self._right_move, self._down_move, self._up_move]
        else:
            self._basic_moves = [self._left_move, self._right_move, self._up_move, self._down_move]
        if position in diagonal_points:
            diagonals = self.diagonals(position, 1)
            self._basic_moves += diagonals


class General(Palace):
    """
    A child of the Palace class. Contains no unique logic, but is used by the Game class to determine whether
    a player is in check or checkmate. It is created by the Board class at the start of a game instance.
    """
    def __init__(self, position, player):
        """
        Same as Palace initialization - simply inherits from it using super() (i.e., no special logic)
        :param position: the tile that the piece starts on - should be a key in the board dictionary
        :param player: the Player object that the piece should be associated to
        """
        super().__init__(position, player)

    def __str__(self):
        """
        An override of the str dunder method for use in the Game class when determining what type of piece is
        being handled
        :return: Returns the string 'general'
        """
        return 'general'


class Guard(Palace):
    """
    A child of the Palace class. Contains no unique logic, but is differentiated from the General class so that
    the Game object knows which piece to use when determining check or checkmate. It is created by the Board class
    at the start of a game instance.
    """
    def __init__(self, position, player):
        """
        Same as Palace initialization - simply inherits from it using super() (i.e., no special logic)
        :param position: the tile that the piece starts on - should be a key in the board dictionary
        :param player: the Player object that the piece should be associated to
        """
        super().__init__(position, player)

    def __str__(self):
        """
        An override of the str dunder method for use in the Game class when determining what type of piece is
        being handled
        :return: Returns the string 'guard'
        """
        return 'guard'
