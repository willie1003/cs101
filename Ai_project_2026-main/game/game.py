"""
Game state and rule enforcement for EZChess.
"""

from game.board import Board
from game.piece import Piece


class MoveRecord:
    """A single move record."""

    def __init__(self, src, dst, piece, captured=None, points=0, elapsed=0):
        self.src = src
        self.dst = dst
        self.piece = piece
        self.captured = captured
        self.points = points
        self.elapsed = elapsed


class GameState:
    """Tracks board state, timing, scoring, and turn order."""

    MAX_ROUNDS = 20
    TIME_NORMAL = 60
    TIME_EXTENDED = 120
    MAX_EXTENDS = 3
    SLOW_FORFEIT_CNT = 4

    def __init__(self):
        self.board = Board()
        self.round_num = 0
        self.current_side = "UV"
        self.ab_points = 0
        self.uv_points = 0
        self.ab_time = 0
        self.uv_time = 0
        self.time_extends = {"AB": 3, "UV": 3}
        self.slow_responses = {"AB": 0, "UV": 0}
        self.moves_history = []
        self.initial_move_done = False
        self.forfeit_side = None
        self.game_ended = False

    def setup_game(self, initial_move=None):
        """Apply the optional opening rearrangement."""
        if initial_move:
            src, dst = initial_move
            self.apply_initial_rearrangement(src, dst, 0)

    def get_initial_rearrangements(self):
        """
        Return all legal opening rearrangements.

        Rule: UV may move any one piece on the board to any empty square.
        """
        moves = []

        for src_row in range(8):
            for src_col in range(8):
                piece = self.board.get_piece(src_row, src_col)
                if piece == "+":
                    continue

                for dst_row in range(8):
                    for dst_col in range(8):
                        if self.board.get_piece(dst_row, dst_col) == "+":
                            moves.append(((src_row, src_col), (dst_row, dst_col)))

        return moves

    def _apply_time_rule(self, side, elapsed):
        """Update clocks and forfeit state for one response."""
        if side == "AB":
            self.ab_time += elapsed
        else:
            self.uv_time += elapsed

        if elapsed > self.TIME_EXTENDED:
            self.forfeit_side = side
            self.game_ended = True
            return False

        if elapsed > self.TIME_NORMAL:
            self.time_extends[side] -= 1
            self.slow_responses[side] += 1
            if self.slow_responses[side] >= self.SLOW_FORFEIT_CNT:
                self.forfeit_side = side
                self.game_ended = True
                return False
            if self.time_extends[side] < 0:
                self.forfeit_side = side
                self.game_ended = True
                return False

        return True

    def apply_initial_rearrangement(self, src, dst, elapsed):
        """
        Apply UV's opening rearrangement.

        This move is timed and counts as UV's first response.
        """
        if self.forfeit_side or self.initial_move_done:
            return None

        src_row, src_col = src
        dst_row, dst_col = dst
        piece = self.board.get_piece(src_row, src_col)
        target = self.board.get_piece(dst_row, dst_col)

        if not piece or piece == "+":
            return None
        if target != "+":
            return None

        self.board.set_piece(src_row, src_col, "+")
        self.board.set_piece(dst_row, dst_col, piece)

        if not self._apply_time_rule("UV", elapsed):
            return None

        move_record = MoveRecord(src, dst, piece, None, 0, elapsed)
        self.moves_history.append(move_record)
        self.initial_move_done = True
        self.round_num = 1
        self.current_side = "AB"
        return move_record

    def apply_move(self, src, dst, elapsed, is_initial=False):
        """Apply one regular move."""
        if is_initial:
            return self.apply_initial_rearrangement(src, dst, elapsed)

        if self.forfeit_side:
            return None

        src_row, src_col = src
        dst_row, dst_col = dst
        piece = self.board.get_piece(src_row, src_col)

        if not piece or piece == "+":
            return None

        side = Piece.get_side(piece)
        if side != self.current_side:
            return None

        valid_moves = Piece.get_moves(piece, src_row, src_col, self.board)
        if (dst_row, dst_col) not in valid_moves:
            return None

        captured_piece = self.board.get_piece(dst_row, dst_col)
        points = 0
        if captured_piece != "+":
            points = Piece.get_points(captured_piece)

        self.board.set_piece(src_row, src_col, "+")
        self.board.set_piece(dst_row, dst_col, piece)

        if side == "AB":
            self.ab_points += points
        else:
            self.uv_points += points

        if not self._apply_time_rule(side, elapsed):
            return None

        move_record = MoveRecord(src, dst, piece, captured_piece, points, elapsed)
        self.moves_history.append(move_record)

        if self.current_side == "UV":
            self.round_num += 1

        self.current_side = "UV" if self.current_side == "AB" else "AB"

        if self.round_num > self.MAX_ROUNDS:
            self.game_ended = True

        return move_record

    def get_valid_moves(self, side):
        """Return all legal moves for one side."""
        moves = []
        pieces = self.board.get_all_pieces(side)

        for (row, col), piece in pieces.items():
            valid_dests = Piece.get_moves(piece, row, col, self.board)
            for dst in valid_dests:
                moves.append(((row, col), dst))

        return moves

    def is_game_over(self):
        """Return whether the game is over."""
        return self.game_ended or self.forfeit_side is not None

    def get_winner(self):
        """Return the winner and the reason."""
        if self.forfeit_side:
            loser = self.forfeit_side
            winner = "UV" if loser == "AB" else "AB"
            return (winner, "forfeit")

        if not self.game_ended:
            return None

        if self.ab_points > self.uv_points:
            return ("AB", "points")
        if self.uv_points > self.ab_points:
            return ("UV", "points")

        if self.ab_time < self.uv_time:
            return ("AB", "time")
        if self.uv_time < self.ab_time:
            return ("UV", "time")

        return (None, "draw")

    def get_state_info(self):
        """Return display-friendly state info."""
        return {
            "round": self.round_num,
            "current_side": self.current_side,
            "ab_points": self.ab_points,
            "uv_points": self.uv_points,
            "ab_time": self.ab_time,
            "uv_time": self.uv_time,
            "game_ended": self.game_ended,
            "forfeit_side": self.forfeit_side,
        }

    def copy(self):
        """Copy the current state for AI search."""
        new_state = GameState.__new__(GameState)
        new_state.board = self.board.copy()
        new_state.round_num = self.round_num
        new_state.current_side = self.current_side
        new_state.ab_points = self.ab_points
        new_state.uv_points = self.uv_points
        new_state.ab_time = self.ab_time
        new_state.uv_time = self.uv_time
        new_state.time_extends = self.time_extends.copy()
        new_state.slow_responses = self.slow_responses.copy()
        new_state.moves_history = self.moves_history[:]
        new_state.initial_move_done = self.initial_move_done
        new_state.forfeit_side = self.forfeit_side
        new_state.game_ended = self.game_ended
        return new_state
