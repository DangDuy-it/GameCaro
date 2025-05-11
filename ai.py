import math
import random
import copy
import time

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
    'five_ai': 10000000,      # 5 liên tiếp - thắng
    'open_four_ai': 60000,    # 4 mở hai đầu
    'four_ai': 15000,         # 4 có thể thành 5
    'open_three_ai': 8000,    # 3 mở hai đầu
    'five_human': -10000000,  # 5 liên tiếp - thua
    'open_four_human': -70000, # 4 mở hai đầu
    'four_human': -20000,     # 4 có thể thành 5
    'open_three_human': -10000 # 3 mở hai đầu
}

# Hằng số cho thuật toán
WIN_CONDITION = 5  # Số quân liên tiếp để thắng
MAX_CACHE_SIZE = 20000

# Cache cho các hàm
pattern_cache = {}
eval_cache = {}
minimax_cache = {}

def detect_pattern(board, size, directions, player, length, open_ends_required):
    """
    Phát hiện các mẫu với độ dài và số đầu mở cụ thể.
    """
    board_str = ''.join([''.join([str(cell) for cell in row]) for row in board])
    cache_key = (board_str, player, length, open_ends_required)
    if cache_key in pattern_cache:
        return pattern_cache[cache_key]
    
    count = 0
    for i in range(size):
        for j in range(size):
            if board[i][j] != player:
                continue
            is_near = False
            for di in range(-AI_SEARCH_RADIUS, AI_SEARCH_RADIUS + 1):
                for dj in range(-AI_SEARCH_RADIUS, AI_SEARCH_RADIUS + 1):
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < size and 0 <= nj < size and board[ni][nj] != EMPTY:
                        is_near = True
                        break
                if is_near:
                    break
            if not is_near:
                continue
            
            for dx, dy in directions:
                if i - dx >= 0 and j - dy >= 0 and board[i-dx][j-dy] == player:
                    continue
                consecutive = 0
                x, y = i, j
                while 0 <= x < size and 0 <= y < size and board[x][y] == player:
                    consecutive += 1
                    x += dx
                    y += dy
                if consecutive == length:
                    open_ends = 0
                    if i - dx >= 0 and j - dy >= 0 and board[i-dx][j-dy] == EMPTY:
                        open_ends += 1
                    if 0 <= x < size and 0 <= y < size and board[x][y] == EMPTY:
                        open_ends += 1
                    if open_ends >= open_ends_required:
                        count += 1
    
    pattern_cache[cache_key] = count
    return count

def count_consecutive(board, size, x, y, dx, dy, player):
    count = 0
    for i in range(WIN_CONDITION):
        nx, ny = x + i*dx, y + i*dy
        if 0 <= nx < size and 0 <= ny < size and board[nx][ny] == player:
            count += 1
        else:
            break
    return count

def count_open_ends(board, size, x, y, dx, dy, player, length):
    open_ends = 0
    start_x, start_y = x - dx, y - dy
    if 0 <= start_x < size and 0 <= start_y < size and board[start_x][start_y] == EMPTY:
        open_ends += 1
    end_x, end_y = x + length*dx, y + length*dy
    if 0 <= end_x < size and 0 <= end_y < size and board[end_x][end_y] == EMPTY:
        open_ends += 1
    return open_ends

def evaluate_position(board, player, opponent):
    """
    Đánh giá trạng thái bàn cờ.
    Bỏ broken_three, open_two, điểm trung tâm để tăng tốc.
    """
    board_str = ''.join([''.join([str(cell) for cell in row]) for row in board])
    cache_key = (board_str, player, opponent)
    if cache_key in eval_cache:
        return eval_cache[cache_key]
    
    score = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    size = BOARD_SIZE
    
    if check_win(board, player):
        return 10000000
    if check_win(board, opponent):
        return -10000000
    
    open_four = detect_pattern(board, size, directions, player, 4, 2)
    score += open_four * PATTERN_SCORES['open_four_ai']
    opponent_open_four = detect_pattern(board, size, directions, opponent, 4, 2)
    score += opponent_open_four * PATTERN_SCORES['open_four_human']
    
    semi_open_four = detect_pattern(board, size, directions, player, 4, 1)
    score += semi_open_four * PATTERN_SCORES['four_ai']
    opponent_semi_open_four = detect_pattern(board, size, directions, opponent, 4, 1)
    score += opponent_semi_open_four * PATTERN_SCORES['four_human']
    
    open_three = detect_pattern(board, size, directions, player, 3, 2)
    score += open_three * PATTERN_SCORES['open_three_ai']
    opponent_open_three = detect_pattern(board, size, directions, opponent, 3, 2)
    score += opponent_open_three * PATTERN_SCORES['open_three_human']
    
    eval_cache[cache_key] = score
    return score

def is_winning_move(board, row, col, player):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    size = BOARD_SIZE
    for dx, dy in directions:
        count = 1
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

def get_smart_moves(board, max_moves=MAX_CONSIDERED_MOVES):
    """
    Lấy các nước đi thông minh.
    Đơn giản hóa để tăng tốc.
    """
    size = BOARD_SIZE
    moves = []
    has_pieces = False
    
    for i in range(size):
        for j in range(size):
            if board[i][j] != EMPTY:
                has_pieces = True
                break
        if has_pieces:
            break
    
    if not has_pieces:
        center = size // 2
        return [(center, center)]
    
    winning_moves = []
    blocking_moves = []
    for i in range(size):
        for j in range(size):
            if board[i][j] == EMPTY:
                board_copy = [row[:] for row in board]
                board_copy[i][j] = AI_PLAYER
                if is_winning_move(board_copy, i, j, AI_PLAYER):
                    winning_moves.append((i, j))
                board_copy[i][j] = HUMAN_PLAYER
                if is_winning_move(board_copy, i, j, HUMAN_PLAYER):
                    blocking_moves.append((i, j))
    
    if winning_moves:
        return winning_moves[:max_moves]
    if blocking_moves:
        moves.extend(blocking_moves)
    
    positions_added = set(moves)
    for i in range(size):
        for j in range(size):
            if board[i][j] != EMPTY:
                for distance in [1, 2]:
                    if len(moves) >= max_moves:
                        break
                    for di in range(-distance, distance + 1):
                        for dj in range(-distance, distance + 1):
                            if abs(di) + abs(dj) != distance:
                                continue
                            ni, nj = i + di, j + dj
                            if (0 <= ni < size and 0 <= nj < size and 
                                board[ni][nj] == EMPTY and 
                                (ni, nj) not in positions_added):
                                moves.append((ni, nj))
                                positions_added.add((ni, nj))
                                if len(moves) >= max_moves:
                                    break
    
    if len(moves) < max_moves:
        for i in range(size):
            for j in range(size):
                if board[i][j] == EMPTY and (i, j) not in positions_added:
                    moves.append((i, j))
                    positions_added.add((i, j))
                    if len(moves) >= max_moves:
                        break
    
    random.shuffle(moves)
    return moves[:max_moves]

def get_valid_locations(board, difficulty=DIFFICULTY_EASY):
    return get_smart_moves(board)

def is_terminal_node(board):
    return check_win(board, PLAYER_X) or check_win(board, PLAYER_O) or check_draw(board)

def minimax(board, depth, alpha, beta, is_maximizing_player):
    """
    Thuật toán Minimax với Alpha-Beta pruning.
    Đơn giản hóa move ordering để tăng tốc.
    """
    board_str = ''.join([''.join([str(cell) for cell in row]) for row in board])
    cache_key = (board_str, depth, is_maximizing_player)
    if cache_key in minimax_cache:
        return minimax_cache[cache_key]
    
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    
    if depth == 0 or is_terminal or not valid_locations:
        if is_terminal:
            if check_win(board, AI_PLAYER):
                return (None, 1000000000)
            elif check_win(board, HUMAN_PLAYER):
                return (None, -1000000000)
            else:
                return (None, 0)
        else:
            return (None, evaluate_position(board, AI_PLAYER, HUMAN_PLAYER))
    
    # Ưu tiên nước thắng/chặn
    prioritized_moves = []
    center = BOARD_SIZE // 2
    for (row, col) in valid_locations:
        board_copy = [r[:] for r in board]
        player = AI_PLAYER if is_maximizing_player else HUMAN_PLAYER
        place_piece(board_copy, row, col, player)
        if is_winning_move(board_copy, row, col, player):
            score = 1000000000 if is_maximizing_player else -1000000000
            prioritized_moves.append(((row, col), score))
        else:
            # Ưu tiên ô gần trung tâm
            distance = abs(row - center) + abs(col - center)
            score = -distance
            prioritized_moves.append(((row, col), score))
    
    prioritized_moves.sort(key=lambda x: x[1], reverse=is_maximizing_player)
    valid_locations = [move for move, _ in prioritized_moves]
    
    if is_maximizing_player:
        value = -math.inf
        best_move = None
        for (row, col) in valid_locations:
            board_copy = [r[:] for r in board]
            place_piece(board_copy, row, col, AI_PLAYER)
            _, new_score = minimax(board_copy, depth - 1, alpha, beta, False)
            if new_score > value:
                value = new_score
                best_move = (row, col)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        minimax_cache[cache_key] = (best_move, value)
        return best_move, value
    
    else:
        value = math.inf
        best_move = None
        for (row, col) in valid_locations:
            board_copy = [r[:] for r in board]
            place_piece(board_copy, row, col, HUMAN_PLAYER)
            _, new_score = minimax(board_copy, depth - 1, alpha, beta, True)
            if new_score < value:
                value = new_score
                best_move = (row, col)
            beta = min(beta, value)
            if beta <= alpha:
                break
        minimax_cache[cache_key] = (best_move, value)
        return best_move, value

def get_best_move_with_iterative_deepening(board, max_depth):
    """
    Iterative deepening với độ sâu tối đa 3 và giới hạn thời gian 0.5 giây.
    """
    best_move = None
    minimax_cache.clear()
    pattern_cache.clear()
    eval_cache.clear()
    
    start_time = time.time()
    for current_depth in range(1, min(max_depth, 3) + 1):
        if time.time() - start_time > 0.5:  # Giới hạn 0.5 giây
            break
        move, score = minimax(board, current_depth, -math.inf, math.inf, True)
        if move:
            best_move = move
        if score >= 1000000:
            break
    return best_move

def find_easy_move(board):
    size = BOARD_SIZE
    valid_locations = []
    
    for i in range(size):
        for j in range(size):
            if board[i][j] == EMPTY:
                for di in range(-1, 2):
                    for dj in range(-1, 2):
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < size and 0 <= nj < size and board[ni][nj] != EMPTY:
                            valid_locations.append((i, j))
                            break
                    if len(valid_locations) >= MAX_CONSIDERED_MOVES:
                        break
        if len(valid_locations) >= MAX_CONSIDERED_MOVES:
            break
    
    if not valid_locations:
        for i in range(size):
            for j in range(size):
                if board[i][j] == EMPTY:
                    valid_locations.append((i, j))
                    if len(valid_locations) >= MAX_CONSIDERED_MOVES:
                        break
            if len(valid_locations) >= MAX_CONSIDERED_MOVES:
                break
    
    if not valid_locations:
        return None
    
    for (row, col) in valid_locations:
        board_copy = [row[:] for row in board]
        place_piece(board_copy, row, col, AI_PLAYER)
        if is_winning_move(board_copy, row, col, AI_PLAYER):
            return (row, col)
        board_copy = [row[:] for row in board]
        place_piece(board_copy, row, col, HUMAN_PLAYER)
        if is_winning_move(board_copy, row, col, HUMAN_PLAYER):
            return (row, col)
    
    return random.choice(valid_locations)

def clear_caches():
    pattern_cache.clear()
    eval_cache.clear()
    minimax_cache.clear()

def get_ai_move(board, difficulty_level, depth=None):
    start_time = time.time()
    clear_caches()
    move = None
    if difficulty_level == DIFFICULTY_EASY:
        print("AI (Dễ - Heuristic) đang tính toán...")
        move = find_easy_move(board)
    elif difficulty_level == DIFFICULTY_MEDIUM:
        print(f"AI (Trung Bình - Minimax Depth={MEDIUM_DEPTH}) đang tính toán...")
        move = minimax(board, MEDIUM_DEPTH, -math.inf, math.inf, True)[0]
    elif difficulty_level == DIFFICULTY_HARD:
        print(f"AI (Khó - Minimax Nâng Cao - Depth={HARD_DEPTH}) đang tính toán...")
        move = get_best_move_with_iterative_deepening(board, HARD_DEPTH)
    print(f"Thời gian tính toán: {time.time() - start_time:.3f} giây")
    return move