import torch
import chess
import random
from game.chess.chess_board_translator import ChessBoardTranslator

device = torch.device("cpu")

translator = ChessBoardTranslator(device)

def assert_board_state_pre_view(tensor, i):
    # Pawns
    assert(torch.sum(tensor[i][0]) == 8)
    assert(torch.sum(tensor[i][6]) == 8)

    # Knight
    assert(torch.sum(tensor[i][1]) == 2)
    assert(torch.sum(tensor[i][7]) == 2)

    # Bishop
    assert(torch.sum(tensor[i][2]) == 2)
    assert(torch.sum(tensor[i][8]) == 2)

    # Rook
    assert(torch.sum(tensor[i][3]) == 2)
    assert(torch.sum(tensor[i][9]) == 2)

    # King
    assert(torch.sum(tensor[i][4]) == 1)
    assert(torch.sum(tensor[i][10]) == 1)

    # Queen
    assert(torch.sum(tensor[i][5]) == 1)
    assert(torch.sum(tensor[i][11]) == 1)

def assert_board_state_post_view(tensor, i):
    # Pawns
    assert(torch.sum(tensor[14 * i]) == 8)
    assert(torch.sum(tensor[14 * i + 6]) == 8)

    # Knight
    assert(torch.sum(tensor[14 * i + 1]) == 2)
    assert(torch.sum(tensor[14 * i + 7]) == 2)

    # Bishop
    assert(torch.sum(tensor[14 * i + 2]) == 2)
    assert(torch.sum(tensor[14 * i + 8]) == 2)

    # Rook
    assert(torch.sum(tensor[14 * i + 3]) == 2)
    assert(torch.sum(tensor[14 * i + 9]) == 2)

    # King
    assert(torch.sum(tensor[14 * i + 4]) == 1)
    assert(torch.sum(tensor[14 * i + 10]) == 1)

    # Queen
    assert(torch.sum(tensor[14 * i + 5]) == 1)
    assert(torch.sum(tensor[14 * i + 11]) == 1)

def test_push_into_history():
    tensor = torch.zeros((8, 14, 8, 8))
    board = chess.Board() # default state

    tensor = translator._ChessBoardTranslator__push_into_history(board, tensor, 0)

    assert_board_state_pre_view(tensor, 0)

    board.push(chess.Move.from_uci("g1f3"))
    tensor = translator._ChessBoardTranslator__push_into_history(board, tensor, 1)
    assert_board_state_pre_view(tensor, 1)

def test_encode():
    board = chess.Board()

    # Make moves to build up history
    oldest_state = None
    for i in range(8):
        legal_moves = list(filter(lambda move: not board.is_capture(move), board.legal_moves)) # get all non-capture legal moves
        if not legal_moves: # if no legal moves left, break out of the loop
            break
        move = random.choice(legal_moves) # choose a random non-capture legal move

        board.push(move) # make the move on the board

        if i == 0:
            oldest_state = chess.Board(board.fen())

    newest_state = chess.Board(board.fen())

    # Encode
    tensor = translator.encode(board)

    # Check that the oldest_state and newest move encoded match the return tensor
    oldest_tensor = translator._ChessBoardTranslator__encode_single_board(oldest_state)
    newest_tensor = translator._ChessBoardTranslator__encode_single_board(newest_state)

    # Assert that states match order in resultin g tensor
    # newest is at [0], oldest is at [7]
    print(tensor[98])
    print(oldest_tensor[0])
    assert(torch.allclose(tensor[0:14], newest_tensor))
    assert(torch.allclose(tensor[98:112], oldest_tensor))

    assert(tensor.shape == (119, 8, 8))

    # Check all time steps
    for i in range(8):
        assert_board_state_post_view(tensor, i)

    assert(torch.sum(tensor[112]) == 64)
    assert(torch.sum(tensor[113]) == 5 * 64)

    # can't assert casting rights and no progress counter (not sure because random)
