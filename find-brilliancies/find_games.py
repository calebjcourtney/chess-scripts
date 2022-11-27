"""
Here's the description of brilliant moves from the chess.com site: https://support.chess.com/article/2965-how-are-moves-classified-what-is-a-blunder-or-brilliant-and-etc#:~:text=We%20replaced%20the%20old%20Brilliant,had%20not%20found%20the%20move.
Brilliant (!!) moves and Great Moves are always the best or nearly best move in the position, but are also special in some way.
We replaced the old Brilliant algorithm with a simpler definition
    a Brilliant move is when you find a good piece sacrifice
    you should not be in a bad position after a Brilliant move
    you should not be completely winning even if you had not found the move.
Also, we are more generous in defining a piece sacrifice for newer players, compared with those who are higher rated.
"""

import argparse
from io import StringIO

import requests
from tqdm import tqdm

import chess
import chess.pgn
import chess.engine


PIECE_VALUE_MAP = {
    chess.KING: 0,
    chess.QUEEN: 9,
    chess.KNIGHT: 3,
    chess.ROOK: 5,
    chess.BISHOP: 3,
    chess.PAWN: 1
}


def value_of_defenders(board, move):
    squares = [square for square in board.attackers(board.turn, move.to_square) if square != move.from_square]
    return len(squares)


def value_of_attackers(board, move):
    squares = [square for square in board.attackers(board.turn ^ 1, move.to_square)]
    return len(squares)


def piece_is_underdefended(board, move):
    defenders = value_of_defenders(board, move)
    attackers = value_of_attackers(board, move)

    return attackers > defenders


def piece_is_moved(board, move) -> bool:
    return board.piece_at(move.from_square).piece_type in [
        chess.KNIGHT,
        chess.BISHOP,
        chess.ROOK,
        chess.QUEEN
    ]


def captures_greater_piece(board, move):
    piece_moved_value = PIECE_VALUE_MAP[board.piece_at(move.from_square).piece_type]
    target_square_piece = board.piece_at(move.to_square)
    target_value = PIECE_VALUE_MAP.get(
        None if target_square_piece is None else target_square_piece.piece_type,
        0
    )

    # captures a more valuable piece or a piece of equal value
    return piece_moved_value <= target_value


def move_is_piece_sacrifice(board, move):
    # it is a piece that's moved
    if not piece_is_moved(board, move):
        return False

    # make sure it's not just a capture of another piece
    if captures_greater_piece(board, move):
        return False

    # the square is underdefended
    if not piece_is_underdefended(board, move):
        return False

    return True


def best_move_is_played(move, engine_eval):
    return engine_eval[0]['pv'][0] == move


def losing_if_played(board, engine_eval):
    return engine_eval[0]['score'].pov(board.turn).score(mate_score=100) > 0


def not_completely_winning(board, engine_eval):
    return engine_eval[1]['score'].pov(board.turn).score(mate_score=100) > 0


def move_is_brilliant(board, move, engine):
    if not move_is_piece_sacrifice(board, move):
        return False

    engine_eval = engine.analyse(board, chess.engine.Limit(depth=18), multipv=2)
    uci = board.uci(move)
    if not best_move_is_played(uci, engine_eval):
        return False

    return True


def game_has_brilliant(game, player_color, engine):
    board = game.board()
    for move in game.mainline_moves():
        if board.turn == player_color and move_is_brilliant(board, move, engine):
            return True

        board.push(move)

    return False


def read_game(pgn: StringIO):
    try:
        game = chess.pgn.read_game(pgn)
    except AssertionError:
        return read_game()

    return game


def main(username, engine_path):
    brilliant_games = []
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    archives = requests.get(
        f"https://api.chess.com/pub/player/{username}/games/archives",
        verify=False
    ).json()["archives"]
    archives.sort(reverse=True)

    for url in tqdm(archives):
        pgn_response = requests.get(f"{url}/pgn", verify=False)

        pgn = StringIO(pgn_response.text)

        game = read_game(pgn)

        while game is not None:
            player_color = chess.WHITE if username == game.headers["White"] else chess.BLACK
            if game_has_brilliant(game, player_color, engine):
                print(game.headers["Link"])
                brilliant_games.append(game.headers["Link"])

            game = read_game(pgn)

    print(brilliant_games)

    engine.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("chesscom_username", type=str, help="your chess.com username")
    parser.add_argument("--engine", type=str, default="/usr/local/bin/stockfish", help="path to your stockfish uci engine")

    args = parser.parse_args()

    main(args.chesscom_username, args.engine)
