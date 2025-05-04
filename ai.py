# ai.py
import math
import random
# Import tường minh các hằng số cần thiết từ constants.py
from constants import (
    BOARD_SIZE, EMPTY,
    PLAYER_X, PLAYER_O, AI_PLAYER, HUMAN_PLAYER,
    DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD,
    MEDIUM_DEPTH, HARD_DEPTH,
    MAX_CONSIDERED_MOVES, AI_SEARCH_RADIUS
)
from board import is_valid_location, place_piece, check_draw # Cần các hàm cơ bản về bàn cờ
from win_checker import check_win # Cần hàm kiểm tra thắng

# --- Hàm đánh giá (evaluate) - Sử dụng trong Minimax (Medium/Hard) ---
def evaluate(board):
    """
    Hàm đánh giá trạng thái bàn cờ cho AI_PLAYER (sử dụng trong Minimax).
    Trả về điểm số dựa trên các đường 5, 4, 3, 2 của AI và đối thủ.
    Điểm cao hơn nghĩa là trạng thái có lợi hơn cho AI.
    Đây là một hàm đánh giá RẤT ĐƠN GIẢN cho mục đích minh họa Minimax.
    Một AI mạnh cần hàm đánh giá phức tạp hơn nhiều.
    """
    # Ưu tiên hàng 5 (thắng ngay) - Trường hợp này thường được xử lý ở is_terminal_node,
    # nhưng thêm vào evaluate giúp Minimax tìm đường thắng nhanh hơn.
    if check_win(board, AI_PLAYER):
        return 1000000
    if check_win(board, HUMAN_PLAYER):
        return -1000000

    # Heuristic đơn giản: đếm số lượng các đoạn tiềm năng
    # Lưu ý: Đây là một heuristic rất cơ bản, không đầy đủ cho Gomoku mạnh
    score = 0

    def count_potential_lines(board, player, length):
         count = 0
         target_value = player
         empty_value = EMPTY

         # Check horizontal
         for r in range(BOARD_SIZE):
             for c in range(BOARD_SIZE - length + 1):
                 line = [board[r][c+i] for i in range(length)]
                 # Đếm các đoạn có (length-1) quân và 1 ô trống (ví dụ: XXX0, XX0X, X0XX, 0XXX)
                 if line.count(target_value) == length - 1 and line.count(empty_value) == 1:
                      # Có thể thêm logic kiểm tra xem các đầu có mở không, nhưng đơn giản chỉ đếm sự tồn tại
                      count += 1

         # Check vertical
         for c in range(BOARD_SIZE):
             for r in range(BOARD_SIZE - length + 1):
                  line = [board[r+i][c] for i in range(length)]
                  if line.count(target_value) == length - 1 and line.count(empty_value) == 1:
                       count += 1

         # Check diagonal \
         for r in range(BOARD_SIZE - length + 1):
             for c in range(BOARD_SIZE - length + 1):
                  line = [board[r+i][c+i] for i in range(length)]
                  if line.count(target_value) == length - 1 and line.count(empty_value) == 1:
                       count += 1

         # Check diagonal /
         for r in range(length - 1, BOARD_SIZE):
             for c in range(BOARD_SIZE - length + 1):
                 line = [board[r-i][c+i] for i in range(length)]
                 if line.count(target_value) == length - 1 and line.count(empty_value) == 1:
                      count += 1

         return count # Simplified count

    # Gán điểm dựa trên heuristic đơn giản
    # Điểm số này chỉ là ví dụ rất đơn giản
    score += count_potential_lines(board, AI_PLAYER, 4) * 1000 # 4 quân của AI
    score += count_potential_lines(board, AI_PLAYER, 3) * 100  # 3 quân của AI

    score -= count_potential_lines(board, HUMAN_PLAYER, 4) * 5000 # Chặn 4 quân của người (phạt nặng)
    # score -= count_potential_lines(board, HUMAN_PLAYER, 3) * 200 # Có thể thêm để AI chặn 3s sớm hơn

    return score


# --- Các hàm hỗ trợ AI ---
def get_valid_locations(board):
    """
    Trả về danh sách các ô trống tiềm năng để xét nước đi.
    Giới hạn tìm kiếm xung quanh các quân cờ đã có để tăng tốc.
    Dùng cho cả Easy Heuristic và Minimax.
    """
    locations = []
    occupied_cells = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != EMPTY:
                 occupied_cells.append((r, c))

    search_radius = AI_SEARCH_RADIUS # Lấy từ constants
    considered_locations = set()

    # Nếu không có quân cờ nào (nước đi đầu tiên), thêm ô trung tâm và vài ô xung quanh
    if not occupied_cells:
         # Thêm trung tâm và một vùng nhỏ xung quanh
         center_row, center_col = BOARD_SIZE // 2, BOARD_SIZE // 2
         for dr in range(-1, 2):
             for dc in range(-1, 2):
                  nr, nc = center_row + dr, center_col + dc
                  if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                       considered_locations.add((nr, nc))
    else:
        # Xét các ô trống trong bán kính nhỏ xung quanh các quân cờ đã có
        for r, c in occupied_cells:
            for dr in range(-search_radius, search_radius + 1):
                for dc in range(-search_radius, search_radius + 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                        considered_locations.add((nr, nc))


    locations = list(considered_locations)

    # Sắp xếp các nước đi tiềm năng (ví dụ: ưu tiên gần trung tâm)
    # Điều này có thể giúp Minimax tìm thấy nước tốt sớm hơn (cải thiện pruning)
    # Và làm cho AI Easy chọn nước ngẫu nhiên có "vẻ" hợp lý hơn
    locations.sort(key=lambda loc: (
        abs(loc[0] - BOARD_SIZE//2) + abs(loc[1] - BOARD_SIZE//2), # Gần trung tâm hơn
        random.random() # Thêm yếu tố ngẫu nhiên nhẹ để tránh lặp lại nước đi
        ))

    # Chỉ trả về một số lượng nước đi giới hạn để tăng tốc
    return locations[:MAX_CONSIDERED_MOVES]


def is_terminal_node(board):
    """Kiểm tra xem trạng thái hiện tại là kết thúc game (thắng/thua/hòa)."""
    # Dùng check_win từ win_checker
    return check_win(board, PLAYER_X) or check_win(board, PLAYER_O) or check_draw(board)


# --- Thuật toán Minimax với Alpha-Beta (Dùng cho Medium/Hard) ---
def minimax(board, depth, alpha, beta, is_maximizing_player):
    """
    Thuật toán Minimax với Alpha-Beta Pruning.
    """
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    # Điều kiện dừng
    if depth == 0 or is_terminal:
        if is_terminal:
            # Điểm cực cao/thấp cho trạng thái kết thúc
            if check_win(board, AI_PLAYER):
                return (None, 1000000000) # AI thắng
            elif check_win(board, HUMAN_PLAYER):
                return (None, -1000000000) # Người chơi thắng
            else: # Hòa
                return (None, 0)
        else: # Độ sâu = 0
            return (None, evaluate(board)) # Dùng hàm evaluate cho Minimax

    if is_maximizing_player:
        value = -math.inf
        best_move = random.choice(valid_locations) if valid_locations else None # Nước đi mặc định

        for (row, col) in valid_locations:
            # Tạo bản sao bàn cờ để thử nước đi
            b_copy = [r[:] for r in board] # Deep copy
            place_piece(b_copy, row, col, AI_PLAYER)
            # Gọi đệ quy cho người chơi (Min player)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            # Hoàn tác nước đi (không cần nếu dùng bản sao)

            if new_score > value:
                value = new_score
                best_move = (row, col)
            alpha = max(alpha, value)
            if alpha >= beta:
                break # Alpha-Beta pruning

        return best_move, value
    else: # is_minimizing_player (Human player)
        value = math.inf
        best_move = random.choice(valid_locations) if valid_locations else None # Nước đi mặc định

        for (row, col) in valid_locations:
            # Tạo bản sao bàn cờ
            b_copy = [r[:] for r in board]
            place_piece(b_copy, row, col, HUMAN_PLAYER)
            # Gọi đệ quy cho AI (Max player)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            # Hoàn tác nước đi

            if new_score < value:
                value = new_score
                best_move = (row, col)
            beta = min(beta, value)
            if beta <= alpha:
                break # Alpha-Beta pruning

        return best_move, value

# --- Thuật toán Heuristic đơn giản (Dùng cho Easy) ---
def find_easy_move(board):
    """
    Tìm nước đi cho AI ở chế độ Dễ sử dụng heuristic đơn giản:
    1. Thắng ngay nếu có thể.
    2. Chặn nước thắng ngay của đối thủ nếu cần.
    3. Ngược lại, chọn một ô trống ngẫu nhiên (từ danh sách giới hạn của get_valid_locations).
    """
    valid_locations = get_valid_locations(board) # Sử dụng danh sách giới hạn

    if not valid_locations:
        return None # Không còn ô trống

    # 1. Kiểm tra nước đi thắng ngay cho AI
    for (row, col) in valid_locations:
        b_copy = [r[:] for r in board] # Tạo bản sao để thử
        place_piece(b_copy, row, col, AI_PLAYER)
        if check_win(b_copy, AI_PLAYER):
            # Không cần hoàn tác b_copy, chỉ trả về nước đi
            return (row, col)

    # 2. Kiểm tra nước đi chặn thắng ngay của người chơi
    for (row, col) in valid_locations:
        b_copy = [r[:] for r in board] # Tạo bản sao để thử
        place_piece(b_copy, row, col, HUMAN_PLAYER) # Thử nước đi của người
        if check_win(b_copy, HUMAN_PLAYER):
            # Nước này cần chặn
            return (row, col)

    # 3. Nếu không có nước thắng/chặn khẩn cấp, chọn ngẫu nhiên một nước hợp lệ
    # valid_locations đã được giới hạn và sắp xếp một phần, chọn ngẫu nhiên từ đây
    # sẽ cho nước đi "có vẻ" hợp lý hơn so với chọn ngẫu nhiên toàn bàn cờ
    return random.choice(valid_locations)


# --- Hàm gọi AI chính dựa trên mức độ khó ---
def get_ai_move(board, difficulty_level, depth):
    """
    Chọn và thực thi thuật toán AI dựa trên mức độ khó đã chọn.

    Args:
        board: Trạng thái bàn cờ hiện tại.
        difficulty_level: Mức độ khó đã chọn (DIFFICULTY_EASY, MEDIUM, HARD).
        depth: Độ sâu tìm kiếm (chỉ dùng cho MEDIUM/HARD).

    Returns:
        Tuple (row, col) là nước đi của AI, hoặc None nếu không tìm được.
    """
    if difficulty_level == DIFFICULTY_EASY:
        # Chế độ Dễ dùng thuật toán heuristic đơn giản
        print("AI (Dễ - Heuristic) đang tính toán...")
        return find_easy_move(board)
    elif difficulty_level == DIFFICULTY_MEDIUM or difficulty_level == DIFFICULTY_HARD:
        # Chế độ Trung bình/Khó dùng Minimax với độ sâu tương ứng
        print(f"AI ({'Trung Bình' if difficulty_level == DIFFICULTY_MEDIUM else 'Khó'} - Minimax Depth={depth}) đang tính toán...")
        # minimax trả về tuple (move, score), chỉ lấy move [0]
        return minimax(board, depth, -math.inf, math.inf, True)[0]
    else:
        return None # Trường hợp mức độ khó không xác định hoặc lỗi