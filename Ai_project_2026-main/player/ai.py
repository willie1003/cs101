"""
Minimax AI with alpha-beta pruning.
"""

from game.piece import Piece
from player.player import Player


class MinimaxAI(Player):
    """Minimax + alpha-beta AI."""

    def __init__(self, side, depth=3):
        super().__init__(side)
        self.depth = depth
        self.opponent_side = "UV" if side == "AB" else "AB"

    def choose_move(self, state):
        valid_moves = state.get_valid_moves(self.side)
        if not valid_moves:
            return None
        if len(valid_moves) == 1:
            return valid_moves[0]

        best_move = None
        best_score = float("-inf")

        for move in valid_moves:
            state_copy = state.copy()
            src, dst = move
            piece = state_copy.board.get_piece(src[0], src[1])
            captured = state_copy.board.get_piece(dst[0], dst[1])
            points = Piece.get_points(captured) if captured != "+" else 0

            state_copy.board.set_piece(src[0], src[1], "+")
            state_copy.board.set_piece(dst[0], dst[1], piece)

            if self.side == "AB":
                state_copy.ab_points += points
            else:
                state_copy.uv_points += points

            state_copy.round_num += 1
            state_copy.current_side = self.opponent_side

            score = self.minimax(
                state_copy,
                self.depth - 1,
                float("-inf"),
                float("inf"),
                False,
            )

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def choose_initial_rearrangement(self, state):
        valid_moves = state.get_initial_rearrangements()
        if not valid_moves:
            return None

        best_move = None
        best_score = float("-inf")

        for move in valid_moves:
            state_copy = state.copy()
            src, dst = move
            if state_copy.apply_initial_rearrangement(src, dst, 0) is None:
                continue

            score = self.minimax(
                state_copy,
                max(self.depth - 1, 0),
                float("-inf"),
                float("inf"),
                False,
            )

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, state, depth, alpha, beta, is_maximizing):
        if depth == 0 or state.is_game_over():
            return self.evaluate(state)

        valid_moves = state.get_valid_moves(state.current_side)
        if not valid_moves:
            return self.evaluate(state)

        if is_maximizing:
            max_score = float("-inf")
            for move in valid_moves:
                state_copy = state.copy()
                src, dst = move
                piece = state_copy.board.get_piece(src[0], src[1])
                captured = state_copy.board.get_piece(dst[0], dst[1])
                points = Piece.get_points(captured) if captured != "+" else 0

                state_copy.board.set_piece(src[0], src[1], "+")
                state_copy.board.set_piece(dst[0], dst[1], piece)

                if state_copy.current_side == "AB":
                    state_copy.ab_points += points
                else:
                    state_copy.uv_points += points

                state_copy.current_side = "UV" if state_copy.current_side == "AB" else "AB"

                score = self.minimax(state_copy, depth - 1, alpha, beta, False)
                max_score = max(max_score, score)
                alpha = max(alpha, score)

                if beta <= alpha:
                    break

            return max_score

        min_score = float("inf")
        for move in valid_moves:
            state_copy = state.copy()
            src, dst = move
            piece = state_copy.board.get_piece(src[0], src[1])
            captured = state_copy.board.get_piece(dst[0], dst[1])
            points = Piece.get_points(captured) if captured != "+" else 0

            state_copy.board.set_piece(src[0], src[1], "+")
            state_copy.board.set_piece(dst[0], dst[1], piece)

            if state_copy.current_side == "AB":
                state_copy.ab_points += points
            else:
                state_copy.uv_points += points

            state_copy.current_side = "UV" if state_copy.current_side == "AB" else "AB"

            score = self.minimax(state_copy, depth - 1, alpha, beta, True)
            min_score = min(min_score, score)
            beta = min(beta, score)

            if beta <= alpha:
                break

        return min_score

    def evaluate(self, state):
        ab_score = state.ab_points
        uv_score = state.uv_points
        score_diff = (ab_score - uv_score) * 10

        ab_value = 0
        uv_value = 0

        for row in range(8):
            for col in range(8):
                piece = state.board.get_piece(row, col)
                if piece != "+":
                    value = Piece.get_value(piece)
                    side = Piece.get_side(piece)
                    if side == "AB":
                        ab_value += value
                    else:
                        uv_value += value

        value_diff = (ab_value - uv_value) * 5

        ab_heat = 0
        uv_heat = 0

        for row in range(8):
            for col in range(8):
                piece = state.board.get_piece(row, col)
                if piece != "+":
                    center_dist = max(abs(row - 3.5), abs(col - 3.5))
                    heat_value = max(0, 4 - center_dist) * 0.5

                    side = Piece.get_side(piece)
                    if side == "AB":
                        ab_heat += heat_value
                    else:
                        uv_heat += heat_value

        heat_diff = (ab_heat - uv_heat) * 0.5

        ab_moves = len(state.get_valid_moves("AB")) if state.current_side == "AB" else 0
        uv_moves = len(state.get_valid_moves("UV")) if state.current_side == "UV" else 0
        mobility_diff = (ab_moves - uv_moves) * 0.3

        total = score_diff + value_diff + heat_diff + mobility_diff

        if self.side == "AB":
            return total
        return -total
