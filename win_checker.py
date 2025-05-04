# win_checker.py
from constants import BOARD_SIZE

def check_win(board, player):
    """Kiểm tra xem người chơi 'player' có thắng chưa (5 quân liên tiếp)."""
    # Chiều ngang
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE - 4):
            if board[row][col] == player and \
               board[row][col+1] == player and \
               board[row][col+2] == player and \
               board[row][col+3] == player and \
               board[row][col+4] == player:
                return True

    # Chiều dọc
    for row in range(BOARD_SIZE - 4):
        for col in range(BOARD_SIZE):
            if board[row][col] == player and \
               board[row+1][col] == player and \
               board[row+2][col] == player and \
               board[row+3][col] == player and \
               board[row+4][col] == player:
                return True

    # Đường chéo chính (\)
    for row in range(BOARD_SIZE - 4):
        for col in range(BOARD_SIZE - 4):
            if board[row][col] == player and \
               board[row+1][col+1] == player and \
               board[row+2][col+2] == player and \
               board[row+3][col+3] == player and \
               board[row+4][col+4] == player:
                return True

    # Đường chéo phụ (/)
    for row in range(4, BOARD_SIZE):
        for col in range(BOARD_SIZE - 4):
            if board[row][col] == player and \
               board[row-1][col+1] == player and \
               board[row-2][col+2] == player and \
               board[row-3][col+3] == player and \
               board[row-4][col+4] == player:
                return True

    return False