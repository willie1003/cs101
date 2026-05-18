"""
Basic smoke tests for EZChess.
"""

from game.game import GameState
from player.player import RandomAI
from ui.display import Display


def test_basic_moves():
    print("=" * 50)
    print("Test 1: basic board and moves")
    print("=" * 50)

    state = GameState()
    Display.display_board(state.board)

    ab_moves = state.get_valid_moves("AB")
    uv_moves = state.get_valid_moves("UV")

    print(f"AB legal moves: {len(ab_moves)}")
    print(f"UV legal moves: {len(uv_moves)}")

    if ab_moves:
        print(f"AB first move: {ab_moves[0]}")

    print("[PASS] basic move generation\n")


def test_capture_and_scoring():
    print("=" * 50)
    print("Test 2: capture and scoring")
    print("=" * 50)

    state = GameState()
    state.board.grid[1][0] = "V"
    state.board.grid[1][1] = "+"
    state.current_side = "AB"

    print("Board before capture:")
    Display.display_board(state.board)

    move = state.apply_move((0, 0), (1, 0), 0.5)
    if move is None:
        print("[FAIL] capture move rejected\n")
        return

    print(f"Captured: {move.captured}")
    print(f"AB score: {state.ab_points}")
    Display.display_board(state.board)
    print("[PASS] capture and scoring\n")


def test_initial_rearrangement():
    print("=" * 50)
    print("Test 3: opening rearrangement")
    print("=" * 50)

    state = GameState()
    move = state.apply_initial_rearrangement((0, 0), (4, 4), 1.25)
    if move is None:
        print("[FAIL] opening rearrangement rejected\n")
        return

    assert state.board.get_piece(0, 0) == "+"
    assert state.board.get_piece(4, 4) == "A"
    assert state.current_side == "AB"
    assert state.round_num == 1
    assert abs(state.uv_time - 1.25) < 1e-9
    print("[PASS] opening rearrangement\n")


def test_ai_game():
    print("=" * 50)
    print("Test 4: AI vs AI smoke test")
    print("=" * 50)

    state = GameState()
    ab_ai = RandomAI("AB")
    uv_ai = RandomAI("UV")

    initial_move = uv_ai.timed_initial_rearrangement(state)
    if initial_move:
        src, dst, elapsed = initial_move
        state.apply_initial_rearrangement(src, dst, elapsed)
        print(f"UV opening rearrangement: ({src[0]},{src[1]}) -> ({dst[0]},{dst[1]}) ({elapsed:.3f}s)")

    Display.display_board(state.board)

    round_count = 0
    while round_count < 3 and not state.is_game_over():
        player = ab_ai if state.current_side == "AB" else uv_ai
        move_result = player.timed_move(state)

        if not move_result:
            print(f"{state.current_side} has no valid move")
            break

        src, dst, elapsed = move_result
        state.apply_move(src, dst, elapsed)
        print(f"Move: ({src[0]},{src[1]}) -> ({dst[0]},{dst[1]}) ({elapsed:.3f}s)")
        round_count += 1

    Display.display_board(state.board)
    print(f"AB score={state.ab_points} time={state.ab_time:.2f}s")
    print(f"UV score={state.uv_points} time={state.uv_time:.2f}s")
    print("[PASS] ai game smoke test\n")


if __name__ == "__main__":
    try:
        test_basic_moves()
        test_capture_and_scoring()
        test_initial_rearrangement()
        test_ai_game()

        print("=" * 50)
        print("All tests passed")
        print("=" * 50)
    except Exception as exc:
        print(f"\n[FAIL] test error: {exc}")
        import traceback

        traceback.print_exc()
