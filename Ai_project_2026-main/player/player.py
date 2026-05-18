"""
Player implementations and move-timing helpers.
"""

import random

from game.piece import Piece
from utils.timer import Timer


class Player:
    """Base player class."""

    def __init__(self, side):
        self.side = side
        self.timer = Timer()

    def choose_move(self, state):
        raise NotImplementedError

    def choose_initial_rearrangement(self, state):
        raise NotImplementedError

    def timed_move(self, state):
        self.timer.start()
        move = self.choose_move(state)
        elapsed = self.timer.stop()

        if move is None:
            return None

        src, dst = move
        return (src, dst, elapsed)

    def timed_initial_rearrangement(self, state):
        self.timer.start()
        move = self.choose_initial_rearrangement(state)
        elapsed = self.timer.stop()

        if move is None:
            return None

        src, dst = move
        return (src, dst, elapsed)


class HumanPlayer(Player):
    """Human-controlled player."""

    @staticmethod
    def _parse_move_input(prompt):
        move_str = input(prompt).strip()
        if move_str.lower() == "quit":
            return None

        parts = move_str.split(",")
        if len(parts) != 4:
            raise ValueError("expected four comma-separated integers")

        src_row, src_col, dst_row, dst_col = map(int, parts)
        return ((src_row, src_col), (dst_row, dst_col))

    def choose_move(self, state):
        while True:
            try:
                move = self._parse_move_input(
                    f"Input move for {self.side} (src_row,src_col,dst_row,dst_col): "
                )
                if move is None:
                    return None

                src, dst = move
                piece = state.board.get_piece(src[0], src[1])
                if piece == "+" or Piece.get_side(piece) != self.side:
                    print("Source square must contain one of your pieces.")
                    continue

                valid_moves = Piece.get_moves(piece, src[0], src[1], state.board)
                if dst not in valid_moves:
                    print("Illegal move.")
                    continue

                return move
            except ValueError:
                print("Format error. Use src_row,src_col,dst_row,dst_col")

    def choose_initial_rearrangement(self, state):
        while True:
            try:
                move = self._parse_move_input(
                    "Input opening rearrangement (src_row,src_col,dst_row,dst_col): "
                )
                if move is None:
                    return None

                src, dst = move
                piece = state.board.get_piece(src[0], src[1])
                target = state.board.get_piece(dst[0], dst[1])
                if piece in (None, "+"):
                    print("Source square must contain a piece.")
                    continue
                if target != "+":
                    print("Destination must be an empty square.")
                    continue

                return move
            except ValueError:
                print("Format error. Use src_row,src_col,dst_row,dst_col")


class RandomAI(Player):
    """Random-move AI."""

    def choose_move(self, state):
        valid_moves = state.get_valid_moves(self.side)
        if not valid_moves:
            return None
        return random.choice(valid_moves)

    def choose_initial_rearrangement(self, state):
        valid_moves = state.get_initial_rearrangements()
        if not valid_moves:
            return None
        return random.choice(valid_moves)
