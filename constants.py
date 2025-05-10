# constants.py

# --- Cài đặt cấu hình game ---
BOARD_SIZE = 19 # Kích thước bàn cờ (19x19)
CELL_SIZE = 30  # Kích thước mỗi ô vuông (pixel)
GUI_MARGIN = 50 # Khoảng lề xung quanh bàn cờ
SCREEN_WIDTH = BOARD_SIZE * CELL_SIZE + 2 * GUI_MARGIN
SCREEN_HEIGHT = BOARD_SIZE * CELL_SIZE + 2 * GUI_MARGIN
LINE_THICKNESS = 1
PIECE_SIZE = CELL_SIZE // 2 - 2 # Kích thước quân cờ

CONNECT_N=5
# --- Màu sắc ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0) # <-- Đảm bảo dòng này tồn tại và đúng
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BOARD_COLOR = (200, 150, 100) # Màu gỗ cho bàn cờ

# --- Trạng thái Game ---
MENU_MAIN = 0
MENU_DIFFICULTY = 1
PLAYING = 2
GAME_OVER = 3
QUIT = 4

# --- Cài đặt người chơi ---
PLAYER_X = 1 # Giá trị cho quân X
PLAYER_O = -1 # Giá trị cho quân O
EMPTY = 0

# --- Định nghĩa vai trò người chơi (cho chế độ PvAI) ---
HUMAN_PLAYER = PLAYER_X # Người chơi là X
AI_PLAYER = PLAYER_O # Máy là O

# --- Mức độ khó AI ---
DIFFICULTY_EASY = 0
DIFFICULTY_MEDIUM = 1
DIFFICULTY_HARD = 2

# --- Cài đặt AI (Độ sâu cho Minimax) ---
# Độ sâu tìm kiếm cho các mức độ khó (chỉ dùng cho Medium và Hard)
MEDIUM_DEPTH = 2
HARD_DEPTH = 3

# Số lượng nước đi tiềm năng tối đa AI xét ở mỗi bước (cho cả Heuristic và Minimax)
MAX_CONSIDERED_MOVES = 25
# Bán kính tìm kiếm ô trống xung quanh quân cờ đã có (để giới hạn không gian tìm kiếm cho AI)
AI_SEARCH_RADIUS = 3

# --- Cài đặt Menu (Chung) ---
BUTTON_WIDTH = 250
BUTTON_HEIGHT = 60
BUTTON_COLOR = (150, 200, 255)
BUTTON_HOVER_COLOR = (100, 150, 255)
BUTTON_TEXT_COLOR = BLACK # <-- Dòng sử dụng BLACK

# --- Cài đặt In-game Menu (Thêm mới) ---
INGAME_MENU_WIDTH = 300
INGAME_MENU_HEIGHT = 300
INGAME_MENU_COLOR = (220, 220, 220) # Màu nền menu
INGAME_MENU_BORDER_COLOR = BLACK # <-- Dòng sử dụng BLACK
INGAME_MENU_BUTTON_WIDTH = 200
INGAME_MENU_BUTTON_HEIGHT = 50
INGAME_MENU_BUTTON_GAP = 15

# Vị trí nút mở menu
MENU_BUTTON_SIZE = 40
MENU_BUTTON_MARGIN = 10