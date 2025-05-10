import math
import random
import copy
# Import tường minh các hằng số cần thiết từ constants.py
from constants import (
    BOARD_SIZE, EMPTY,
    PLAYER_X, PLAYER_O, AI_PLAYER, HUMAN_PLAYER,
    DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD,
    MEDIUM_DEPTH, HARD_DEPTH,
    MAX_CONSIDERED_MOVES, AI_SEARCH_RADIUS
)
from board import is_valid_location, place_piece, check_draw
from win_checker import check_win

# Giá trị điểm cho các mẫu khác nhau
PATTERN_SCORES = {
    # Các mẫu của AI - đánh giá tích cực
    'five_ai': 10000000,      # 5 liên tiếp - thắng
    'open_four_ai': 50000,    # 4 mở hai đầu (rất mạnh)
    'four_ai': 10000,         # 4 có thể thành 5
    'open_three_ai': 5000,    # 3 mở hai đầu
    'three_ai': 1000,         # 3 có thể thành 4
    'open_two_ai': 500,       # 2 mở hai đầu
    'two_ai': 100,            # 2 có thể thành 3
    
    # Các mẫu của người chơi - đánh giá tiêu cực (cần chặn)
    'five_human': -10000000,  # 5 liên tiếp - thua
    'open_four_human': -60000, # 4 mở hai đầu (cực kỳ nguy hiểm)
    'four_human': -15000,     # 4 có thể thành 5 (rất cần chặn)
    'open_three_human': -8000, # 3 mở hai đầu (rất nguy hiểm)
    'three_human': -1500,     # 3 có thể thành 4
    'open_two_human': -600,   # 2 mở hai đầu
    'two_human': -100,        # 2 có thể thành 3
}

# Hằng số cho thuật toán
WIN_CONDITION = 5  # Số quân liên tiếp để thắng

# Cache cho việc tính toán mẫu - tối ưu hóa
pattern_cache = {}

def detect_pattern(board, size, directions, player, length, open_ends_required):
    """
    Phát hiện các mẫu với độ dài và số đầu mở cụ thể.
    Trả về số lượng mẫu tìm thấy.
    
    Cải tiến: Sử dụng phương pháp tìm kiếm hiệu quả hơn từ minimax.py
    
    Args:
        board: Bàn cờ hiện tại
        size: Kích thước bàn cờ
        directions: Danh sách các hướng cần kiểm tra
        player: Người chơi cần kiểm tra (AI_PLAYER hoặc HUMAN_PLAYER)
        length: Độ dài mẫu cần tìm
        open_ends_required: Số đầu mở yêu cầu (0, 1, hoặc 2)
    
    Returns:
        Số mẫu tìm thấy thỏa mãn điều kiện
    """
    # Tạo khóa cho cache
    board_str = ''.join([''.join([str(cell) for cell in row]) for row in board])
    cache_key = (board_str, player, length, open_ends_required)
    
    # Kiểm tra xem kết quả đã có trong cache chưa
    if cache_key in pattern_cache:
        return pattern_cache[cache_key]
    
    count = 0
    
    for i in range(size):
        for j in range(size):
            if board[i][j] != player:
                continue
                
            for dx, dy in directions:
                # Kiểm tra xem đây có thể là điểm bắt đầu của một mẫu không
                if i - dx >= 0 and j - dy >= 0 and board[i-dx][j-dy] == player:
                    continue  # Không phải điểm bắt đầu của mẫu
                
                # Đếm số quân liên tiếp
                consecutive = 0
                x, y = i, j
                
                while 0 <= x < size and 0 <= y < size and board[x][y] == player:
                    consecutive += 1
                    x += dx
                    y += dy
                
                if consecutive == length:
                    # Đếm số đầu mở
                    open_ends = 0
                    
                    # Kiểm tra trước mẫu
                    if i - dx >= 0 and j - dy >= 0 and board[i-dx][j-dy] == EMPTY:
                        open_ends += 1
                        
                    # Kiểm tra sau mẫu
                    if 0 <= x < size and 0 <= y < size and board[x][y] == EMPTY:
                        open_ends += 1
                    
                    if open_ends >= open_ends_required:
                        count += 1
    
    # Lưu kết quả vào cache
    pattern_cache[cache_key] = count
    return count

def count_consecutive(board, size, x, y, dx, dy, player):
    """
    Đếm số quân liên tiếp từ vị trí bắt đầu theo một hướng.
    
    Args:
        board: Bàn cờ hiện tại
        size: Kích thước bàn cờ
        x, y: Vị trí bắt đầu
        dx, dy: Hướng kiểm tra
        player: Người chơi cần kiểm tra
    
    Returns:
        Số quân liên tiếp
    """
    count = 0
    for i in range(WIN_CONDITION):
        nx, ny = x + i*dx, y + i*dy
        if 0 <= nx < size and 0 <= ny < size and board[nx][ny] == player:
            count += 1
        else:
            break
    return count

def count_open_ends(board, size, x, y, dx, dy, player, length):
    """
    Đếm số đầu mở cho một chuỗi quân cờ.
    
    Args:
        board: Bàn cờ hiện tại
        size: Kích thước bàn cờ
        x, y: Vị trí bắt đầu
        dx, dy: Hướng kiểm tra
        player: Người chơi cần kiểm tra
        length: Độ dài chuỗi quân cờ
    
    Returns:
        Số đầu mở (0, 1, hoặc 2)
    """
    open_ends = 0
    
    # Kiểm tra trước chuỗi
    start_x, start_y = x - dx, y - dy
    if 0 <= start_x < size and 0 <= start_y < size and board[start_x][start_y] == EMPTY:
        open_ends += 1
        
    # Kiểm tra sau chuỗi
    end_x, end_y = x + length*dx, y + length*dy
    if 0 <= end_x < size and 0 <= end_y < size and board[end_x][end_y] == EMPTY:
        open_ends += 1
        
    return open_ends

# Cache cho hàm evaluate_position để tránh tính toán lại
eval_cache = {}

def evaluate_position(board, player, opponent):
    """
    Đánh giá trạng thái bàn cờ cho người chơi.
    Cải tiến: Thêm caching và tối ưu hóa đánh giá
    
    Args:
        board: Bàn cờ hiện tại
        player: Người chơi đánh giá (AI_PLAYER)
        opponent: Đối thủ (HUMAN_PLAYER)
    
    Returns:
        Điểm số đánh giá vị trí
    """
    # Tạo khóa cho cache
    board_str = ''.join([''.join([str(cell) for cell in row]) for row in board])
    cache_key = (board_str, player, opponent)
    
    # Kiểm tra xem kết quả đã có trong cache chưa
    if cache_key in eval_cache:
        return eval_cache[cache_key]
    
    score = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # ngang, dọc, chéo, chéo ngược
    size = BOARD_SIZE
    
    # Phát hiện thắng/thua - kiểm tra nhanh
    if check_win(board, player):
        eval_cache[cache_key] = 10000000
        return 10000000  # Thắng
    if check_win(board, opponent):
        eval_cache[cache_key] = -10000000
        return -10000000  # Thua
    
    # Phát hiện và đánh giá các mẫu
    # Mở bốn (mối đe dọa rất cao)
    open_four = detect_pattern(board, size, directions, player, 4, 2)
    score += open_four * 50000
    
    # Đối thủ mở bốn (phải chặn)
    opponent_open_four = detect_pattern(board, size, directions, opponent, 4, 2)
    score -= opponent_open_four * 60000  # Ưu tiên cao hơn để chặn
    
    # Bán mở bốn (một bên bị chặn)
    semi_open_four = detect_pattern(board, size, directions, player, 4, 1)
    score += semi_open_four * 10000
    
    # Đối thủ bán mở bốn
    opponent_semi_open_four = detect_pattern(board, size, directions, opponent, 4, 1)
    score -= opponent_semi_open_four * 15000
    
    # Mở ba
    open_three = detect_pattern(board, size, directions, player, 3, 2)
    score += open_three * 5000
    
    # Đối thủ mở ba
    opponent_open_three = detect_pattern(board, size, directions, opponent, 3, 2)
    score -= opponent_open_three * 8000
    
    # Bán mở ba
    semi_open_three = detect_pattern(board, size, directions, player, 3, 1)
    score += semi_open_three * 1000
    
    # Đối thủ bán mở ba
    opponent_semi_open_three = detect_pattern(board, size, directions, opponent, 3, 1)
    score -= opponent_semi_open_three * 1500
    
    # Mở hai
    open_two = detect_pattern(board, size, directions, player, 2, 2)
    score += open_two * 500
    
    # Đối thủ mở hai
    opponent_open_two = detect_pattern(board, size, directions, opponent, 2, 2)
    score -= opponent_open_two * 600
    
    # Thưởng cho kiểm soát trung tâm
    center = size // 2
    for i in range(size):
        for j in range(size):
            if board[i][j] == player:
                # Khoảng cách từ trung tâm (càng gần càng tốt)
                distance = abs(i - center) + abs(j - center)
                score += max(0, (size - distance)) // 2
            elif board[i][j] == opponent:
                # Trừ điểm cho các quân đối thủ ở trung tâm
                distance = abs(i - center) + abs(j - center)
                score -= max(0, (size - distance)) // 3
    
    # Lưu kết quả vào cache
    eval_cache[cache_key] = score
    return score

def is_winning_move(board, row, col, player):
    """
    Kiểm tra xem nước đi có dẫn đến thắng hay không.
    Tối ưu: Chỉ kiểm tra quanh vị trí vừa đặt
    
    Args:
        board: Bàn cờ hiện tại
        row, col: Vị trí nước đi
        player: Người chơi cần kiểm tra
    
    Returns:
        True nếu nước đi dẫn đến thắng, False nếu không
    """
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    size = BOARD_SIZE
    
    for dx, dy in directions:
        count = 1  # Tính cả quân vừa đặt
        
        # Kiểm tra cả hai hướng
        for direction in [1, -1]:
            nx, ny = row, col
            while True:
                nx += direction * dx
                ny += direction * dy
                if (0 <= nx < size and 0 <= ny < size and 
                    board[nx][ny] == player):
                    count += 1
                else:
                    break
                    
        if count >= WIN_CONDITION:
            return True
            
    return False

def get_smart_moves(board):
    """
    Lấy các nước đi thông minh để giảm không gian tìm kiếm.
    Cải tiến: Sử dụng phương pháp từ minimax.py với một số tối ưu hóa thêm
    
    Args:
        board: Bàn cờ hiện tại
    
    Returns:
        Danh sách các nước đi tiềm năng
    """
    size = BOARD_SIZE
    moves = []
    has_pieces = False
    
    # Kiểm tra xem đã có quân trên bàn cờ chưa
    for i in range(size):
        for j in range(size):
            if board[i][j] != EMPTY:
                has_pieces = True
                break
        if has_pieces:
            break
    
    # Nếu không có quân nào, đặt ở gần trung tâm
    if not has_pieces:
        center = size // 2
        return [(center, center)]
    
    # Ưu tiên 1: Kiểm tra nước thắng ngay lập tức cho AI hoặc chặn người chơi
    for i in range(size):
        for j in range(size):
            if board[i][j] == EMPTY:
                # Kiểm tra nước thắng cho AI
                board_copy = [row[:] for row in board]
                board_copy[i][j] = AI_PLAYER
                if is_winning_move(board_copy, i, j, AI_PLAYER):
                    return [(i, j)]  # Trả về ngay lập tức nếu tìm thấy nước thắng
                
                # Kiểm tra chặn nước thắng của người chơi
                board_copy = [row[:] for row in board]
                board_copy[i][j] = HUMAN_PLAYER
                if is_winning_move(board_copy, i, j, HUMAN_PLAYER):
                    moves.insert(0, (i, j))  # Ưu tiên cao nhất nếu là nước chặn
    
    # Nếu đã tìm thấy nước chặn, trả về ngay
    if moves:
        return moves
    
    # Ưu tiên 2: Tìm ô có thể tạo thành các mẫu chiến lược
    for i in range(size):
        for j in range(size):
            if board[i][j] != EMPTY:
                player = board[i][j]
                opponent = PLAYER_O if player == PLAYER_X else PLAYER_X
                
                # Kiểm tra các ô lân cận cho vị trí chiến lược
                for di in range(-1, 2):
                    for dj in range(-1, 2):
                        if di == 0 and dj == 0:
                            continue
                        
                        # Tìm kiếm các mẫu như "XX_X" hoặc "OO_O"
                        for pl in [player, opponent]:  # Kiểm tra cả nước đi của người chơi và chặn đối thủ
                            count = 0
                            empty_pos = None
                            
                            # Kiểm tra tối đa 4 ô theo hướng này
                            for step in range(4):
                                ni = i + di * step
                                nj = j + dj * step
                                
                                if not (0 <= ni < size and 0 <= nj < size):
                                    break
                                
                                if board[ni][nj] == pl:
                                    count += 1
                                elif board[ni][nj] == EMPTY:
                                    if empty_pos is None:  # Chỉ xét ô trống đầu tiên
                                        empty_pos = (ni, nj)
                                else:
                                    # Gặp quân của đối thủ, dừng lại
                                    break
                            
                            # Nếu tìm thấy mẫu chiến lược (3 quân và 1 ô trống)
                            if count >= 3 and empty_pos is not None and empty_pos not in moves:
                                if pl == opponent:  # Ưu tiên chặn đối thủ
                                    moves.insert(0, empty_pos)
                                else:
                                    moves.append(empty_pos)
    
    # Ưu tiên 3: Xét các ô kề với quân hiện tại
    if len(moves) < MAX_CONSIDERED_MOVES:
        positions_added = set(moves)  # Dùng set để kiểm tra nhanh hơn
        for i in range(size):
            for j in range(size):
                if board[i][j] != EMPTY:
                    # Xét theo độ ưu tiên khoảng cách (gần trước)
                    for distance in [1, 2, 3]:
                        if len(moves) >= MAX_CONSIDERED_MOVES:
                            break
                            
                        # Kiểm tra các ô lân cận với khoảng cách distance
                        for di in range(-distance, distance + 1):
                            for dj in range(-distance, distance + 1):
                                # Chỉ xét các ô có tổng khoảng cách Manhattan = distance
                                if abs(di) + abs(dj) != distance:
                                    continue
                                    
                                ni, nj = i + di, j + dj
                                if (0 <= ni < size and 0 <= nj < size and 
                                    board[ni][nj] == EMPTY and 
                                    (ni, nj) not in positions_added):
                                    moves.append((ni, nj))
                                    positions_added.add((ni, nj))
                                    
                                    if len(moves) >= MAX_CONSIDERED_MOVES:
                                        break
    
    # Nếu vẫn không có đủ nước đi, lấy thêm các ô trống
    if not moves:
        for i in range(size):
            for j in range(size):
                if board[i][j] == EMPTY:
                    moves.append((i, j))
                    if len(moves) >= MAX_CONSIDERED_MOVES:
                        break
    
    # Giới hạn số nước đi và xáo trộn để thêm tính ngẫu nhiên
    if len(moves) > MAX_CONSIDERED_MOVES:
        # Lấy một số nước đi đầu tiên (đã được ưu tiên) và xáo trộn phần còn lại
        priority_moves = moves[:MAX_CONSIDERED_MOVES // 3]
        remaining_moves = moves[MAX_CONSIDERED_MOVES // 3:]
        random.shuffle(remaining_moves)
        moves = priority_moves + remaining_moves[:MAX_CONSIDERED_MOVES - len(priority_moves)]
    else:
        random.shuffle(moves)
        
    return moves

def get_valid_locations(board):
    """
    Trả về danh sách các ô trống tiềm năng cho nước đi tiếp theo.
    Sử dụng get_smart_moves để lấy các nước đi thông minh hơn.
    
    Args:
        board: Bàn cờ hiện tại
    
    Returns:
        Danh sách các vị trí hợp lệ
    """
    return get_smart_moves(board)

def is_terminal_node(board):
    """
    Kiểm tra xem trạng thái hiện tại có phải là trạng thái kết thúc không.
    
    Args:
        board: Bàn cờ hiện tại
    
    Returns:
        True nếu game kết thúc, False nếu không
    """
    return check_win(board, PLAYER_X) or check_win(board, PLAYER_O) or check_draw(board)

# Cache cho minimax để tránh tính toán lại các trạng thái giống nhau
minimax_cache = {}

def minimax(board, depth, alpha, beta, is_maximizing_player):
    """
    Thuật toán Minimax với Alpha-Beta pruning, bổ sung caching.
    
    Args:
        board: Bàn cờ hiện tại
        depth: Độ sâu tìm kiếm còn lại
        alpha: Giá trị alpha cho pruning
        beta: Giá trị beta cho pruning
        is_maximizing_player: True nếu là lượt của AI, False nếu là lượt của người chơi
    
    Returns:
        Tuple (move, score) với move là nước đi tốt nhất và score là điểm số
    """
    # Tạo khóa cho cache
    board_str = ''.join([''.join([str(cell) for cell in row]) for row in board])
    cache_key = (board_str, depth, is_maximizing_player)
    
    # Kiểm tra xem kết quả đã có trong cache chưa
    if cache_key in minimax_cache:
        return minimax_cache[cache_key]
    
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    # Điều kiện dừng
    if depth == 0 or is_terminal or not valid_locations:
        if is_terminal:
            if check_win(board, AI_PLAYER):
                return (None, 1000000000)  # AI thắng
            elif check_win(board, HUMAN_PLAYER):
                return (None, -1000000000)  # Người chơi thắng
            else:  # Hòa
                return (None, 0)
        else:
            return (None, evaluate_position(board, AI_PLAYER, HUMAN_PLAYER))

    if is_maximizing_player:
        value = -math.inf
        best_move = None

        for (row, col) in valid_locations:
            board_copy = [r[:] for r in board]  # Deep copy
            place_piece(board_copy, row, col, AI_PLAYER)

            # Kiểm tra nhanh nước thắng
            if is_winning_move(board_copy, row, col, AI_PLAYER):
                minimax_cache[cache_key] = ((row, col), 1000000000)
                return ((row, col), 1000000000)

            _, new_score = minimax(board_copy, depth - 1, alpha, beta, False)

            if new_score > value:
                value = new_score
                best_move = (row, col)

            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Alpha-Beta pruning

        # Lưu kết quả vào cache
        minimax_cache[cache_key] = (best_move, value)
        return best_move, value

    else:  # Minimizing player
        value = math.inf
        best_move = None

        for (row, col) in valid_locations:
            board_copy = [r[:] for r in board]
            place_piece(board_copy, row, col, HUMAN_PLAYER)

            # Kiểm tra nhanh nước thắng
            if is_winning_move(board_copy, row, col, HUMAN_PLAYER):
                minimax_cache[cache_key] = ((row, col), -1000000000)
                return ((row, col), -1000000000)

            _, new_score = minimax(board_copy, depth - 1, alpha, beta, True)

            if new_score < value:
                value = new_score
                best_move = (row, col)

            beta = min(beta, value)
            if beta <= alpha:
                break  # Alpha-Beta pruning

        # Lưu kết quả vào cache
        minimax_cache[cache_key] = (best_move, value)
        return best_move, value

def get_best_move_with_iterative_deepening(board, max_depth):
    """
    Sử dụng iterative deepening để tìm nước đi tốt nhất, với hỗ trợ limit thời gian.
    
    Args:
        board: Bàn cờ hiện tại
        max_depth: Độ sâu tối đa cho tìm kiếm
    
    Returns:
        Nước đi tốt nhất
    """
    best_move = None
    
    # Xóa cache trước khi bắt đầu tìm kiếm mới
    minimax_cache.clear()
    pattern_cache.clear()
    eval_cache.clear()
    
    # Bắt đầu với độ sâu thấp (2) và tăng dần
    for current_depth in range(2, max_depth + 1):
        move, score = minimax(board, current_depth, -math.inf, math.inf, True)
        if move:  # Chỉ cập nhật nếu tìm thấy nước đi
            best_move = move
        
        # Nếu tìm thấy nước thắng, dừng ngay
        if score >= 1000000:
            break
            
    return best_move

def find_easy_move(board):
    """
    Tìm nước đi cho AI ở chế độ Dễ.
    Cải tiến: Tăng hiệu suất bằng cách tối ưu tìm kiếm
    
    Args:
        board: Bàn cờ hiện tại
    
    Returns:
        Nước đi được chọn
    """
    valid_locations = get_valid_locations(board)

    if not valid_locations:
        return None  # Không còn ô trống

    # 1. Kiểm tra nước đi thắng ngay cho AI
    for (row, col) in valid_locations:
        board_copy = [r[:] for r in board]
        place_piece(board_copy, row, col, AI_PLAYER)
        if is_winning_move(board_copy, row, col, AI_PLAYER):
            return (row, col)

    # 2. Kiểm tra nước đi chặn thắng ngay của người chơi
    for (row, col) in valid_locations:
        board_copy = [r[:] for r in board]
        place_piece(board_copy, row, col, HUMAN_PLAYER)
        if is_winning_move(board_copy, row, col, HUMAN_PLAYER):
            return (row, col)

    # 3. Nếu không có nước thắng/chặn khẩn cấp, chọn ngẫu nhiên một nước hợp lệ
    return random.choice(valid_locations)

def clear_caches():
    """
    Xóa tất cả các cache để đảm bảo không giữ lại thông tin từ lượt chơi trước
    """
    pattern_cache.clear()
    eval_cache.clear()
    minimax_cache.clear()

def get_ai_move(board, difficulty_level, depth=None):
    """
    Chọn và thực thi thuật toán AI dựa trên mức độ khó.
    Cải tiến: Xóa cache trước mỗi lần tìm kiếm mới
    
    Args:
        board: Bàn cờ hiện tại
        difficulty_level: Mức độ khó đã chọn
        depth: Độ sâu tìm kiếm (chỉ dùng cho MEDIUM/HARD)
    
    Returns:
        Tuple (row, col) là nước đi của AI, hoặc None n
    """
    if difficulty_level == DIFFICULTY_EASY:
        print("AI (Dễ - Heuristic) đang tính toán...")
        return find_easy_move(board)
    elif difficulty_level == DIFFICULTY_MEDIUM:
        print(f"AI (Trung Bình - Minimax Depth={MEDIUM_DEPTH}) đang tính toán...")
        return minimax(board, MEDIUM_DEPTH, -math.inf, math.inf, True)[0]
    elif difficulty_level == DIFFICULTY_HARD:
        print(f"AI (Khó - Minimax Nâng Cao - Depth={HARD_DEPTH}) đang tính toán...")
        return get_best_move_with_iterative_deepening(board, HARD_DEPTH + 1)
    else:
        return None