"""
EZChess command-line entry point.
"""

import argparse
import sys

from game.game import GameState
from player.ai import MinimaxAI
from player.player import HumanPlayer, RandomAI
from ui.display import Display


def create_player(mode_char, side):
    if mode_char == "h":
        return HumanPlayer(side)
    if mode_char == "r":
        return RandomAI(side)
    if mode_char == "a":
        return MinimaxAI(side, depth=3)
    raise ValueError(f"Unknown player mode: {mode_char}")


def get_initial_move_uv(player, state):
    """Get UV opening rearrangement with timing."""
    print("\n" + "=" * 50)
    print("Opening rearrangement: UV may move any one piece to any empty square.")
    print("=" * 50)

    while True:
        result = player.timed_initial_rearrangement(state)
        if result is None:
            print("Opening rearrangement failed.")
            continue

        src, dst, elapsed = result
        piece = state.board.get_piece(src[0], src[1])
        target = state.board.get_piece(dst[0], dst[1])
        if piece != "+" and target == "+":
            return result

        print("Opening rearrangement must move one piece to an empty square.")


def play_game(ab_player, uv_player, is_initial_move_required=True, depth=3):
    state = GameState()

    if isinstance(ab_player, MinimaxAI):
        ab_player.depth = depth
    if isinstance(uv_player, MinimaxAI):
        uv_player.depth = depth

    print("\n" + "=" * 50)
    print("Game Start")
    print("=" * 50)
    Display.display_board(state.board)

    if is_initial_move_required:
        initial_move = get_initial_move_uv(uv_player, state)
        src, dst, elapsed = initial_move
        piece = state.board.get_piece(src[0], src[1])

        move_record = state.apply_initial_rearrangement(src, dst, elapsed)
        if move_record is None:
            print("UV opening rearrangement invalid or overtime. UV forfeits.")
            state.forfeit_side = "UV"
            state.game_ended = True
        else:
            print(
                f"\nUV opening rearrangement {piece}:"
                f"({src[0]},{src[1]})-({dst[0]},{dst[1]}) | time: {elapsed:.2f}s"
            )
            Display.display_board(state.board)

    while not state.is_game_over():
        Display.display_game_state(state)

        if state.current_side == "AB":
            current_player = ab_player
        else:
            current_player = uv_player

        print(f"Turn: {state.current_side}")

        result = current_player.timed_move(state)
        if result is None:
            print(f"{state.current_side} failed to return a move and forfeits.")
            state.forfeit_side = state.current_side
            state.game_ended = True
            break

        src, dst, elapsed = result
        piece = state.board.get_piece(src[0], src[1])
        captured = state.board.get_piece(dst[0], dst[1])
        move_record = state.apply_move(src, dst, elapsed)

        if move_record is None:
            print(f"{state.current_side} returned an invalid move and forfeits.")
            state.forfeit_side = state.current_side
            state.game_ended = True
            break

        line = f"{piece}:({src[0]},{src[1]})-({dst[0]},{dst[1]})"
        if captured != "+":
            line += f" captured {captured} for {move_record.points} points"
        line += f" | time: {elapsed:.2f}s"
        line += f" | total: AB={state.ab_time:.2f}s UV={state.uv_time:.2f}s"
        print(line)

        Display.display_board(state.board)

    print("\n" + "=" * 50)
    print("Game Over")
    print("=" * 50)

    winner_info = state.get_winner()
    winner, reason = winner_info if winner_info else (None, None)
    Display.display_game_over(winner, reason)

    print(f"Rounds: {state.round_num}")
    print(f"AB score={state.ab_points} time={state.ab_time:.2f}s")
    print(f"UV score={state.uv_points} time={state.uv_time:.2f}s")

    if winner:
        print(f"Winner: {winner}")
    else:
        print("Draw")


def main():
    parser = argparse.ArgumentParser(
        description="EZChess",
        epilog="Modes: h=Human, r=RandomAI, a=MinimaxAI",
    )

    parser.add_argument(
        "--mode",
        type=str,
        default="hh",
        help="Player modes (aa/hh/ha/ah/ra/ar/rr, default: hh)",
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=3,
        help="AI search depth (default: 3)",
    )

    parser.add_argument(
        "--no-initial-move",
        action="store_true",
        help="Skip UV opening rearrangement",
    )

    args = parser.parse_args()

    mode = args.mode.lower()
    if len(mode) != 2 or mode not in ["aa", "hh", "ha", "ah", "ra", "ar", "rr"]:
        print("Invalid mode. Use one of aa/hh/ha/ah/ra/ar/rr")
        print("First char is AB, second char is UV")
        sys.exit(1)

    ab_player = create_player(mode[0], "AB")
    uv_player = create_player(mode[1], "UV")

    try:
        play_game(
            ab_player,
            uv_player,
            is_initial_move_required=not args.no_initial_move,
            depth=args.depth,
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as exc:
        print(f"\n\nRuntime error: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
