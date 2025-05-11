# board.py
from constants import BOARD_SIZE, EMPTY, PLAYER_X, PLAYER_O # Cần PLAYER_X, PLAYER_O để hoàn tác

def create_board():
    """Tạo và trả về một bàn cờ trống."""
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def is_valid_location(board, row, col):
    """Kiểm tra xem ô (row, col) có hợp lệ và trống không."""
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board[row][col] == EMPTY:
        return True
    return False

def place_piece(board, row, col, player):
    """Đặt quân cờ của người chơi vào ô (row, col)."""
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        board[row][col] = player
        return True
    return False

def check_draw(board):
    """Kiểm tra xem bàn cờ đã đầy chưa (hòa)."""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == EMPTY:
                return False # Vẫn còn ô trống
    return True # Bàn cờ đầy

# --- Thêm hàm hoàn tác nước đi ---
def undo_move(board, row, col):
    """Hoàn tác một nước đi tại ô (row, col)."""
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        board[row][col] = EMPTY

