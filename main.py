# main.py
import pygame
import sys
import time

# Import tường minh các hằng số từ constants.py
from constants import (
    MENU_MAIN, MENU_DIFFICULTY, PLAYING, GAME_OVER, QUIT,
    PLAYER_X, PLAYER_O,          # PLAYER_X và PLAYER_O dùng để theo dõi lượt chơi
    HUMAN_PLAYER, AI_PLAYER, # Các vai trò người chơi AI
    DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD, # Các mức độ khó
    MEDIUM_DEPTH, HARD_DEPTH, # Độ sâu cho Minimax
    BUTTON_WIDTH, BUTTON_HEIGHT, # Dùng cho tính toán vị trí nút menu chính
    SCREEN_WIDTH, SCREEN_HEIGHT, GUI_MARGIN, # Dùng cho vị trí trên màn hình
    RED, BLACK, # Màu sắc chung
    MENU_BUTTON_SIZE, MENU_BUTTON_MARGIN # Kích thước/vị trí nút mở menu
)

# Import các module khác
from board import create_board, is_valid_location, place_piece, check_draw, undo_move # Import undo_move
from win_checker import check_win
from graphics import (get_screen, get_font, get_small_font, get_button_font,
                      draw_board, draw_message, get_row_col_from_mouse,
                      draw_turn_message, quit_pygame,
                      draw_main_menu, draw_difficulty_menu,
                      draw_open_menu_button, draw_in_game_menu) # Import các hàm vẽ menu mới
from ai import get_ai_move # Import hàm gọi AI chính


# --- Biến trạng thái game ---
game_state = MENU_MAIN
board = None
current_player = None
game_over = False
winner = None
game_mode = None # 'PvP' hoặc 'PvAI'
ai_level = None # Lưu mức độ khó đã chọn (DIFFICULTY_EASY, MEDIUM, HARD)
ai_search_depth = None # Lưu độ sâu chỉ khi dùng Minimax (Medium/Hard)

# --- Biến trạng thái trong lúc chơi (Thêm mới) ---
is_menu_open = False # Cờ để biết menu trong game có đang mở không
move_history = [] # Lưu lịch sử các nước đi [(row1, col1), (row2, col2), ...]

# --- Vòng lặp chính của game ---
running = True
is_ai_thinking = False # Biến trạng thái để hiển thị "Máy đang nghĩ..." và ngăn click của người

# Lưu trạng thái chuột để vẽ hover cho nút
mouse_pos = (0, 0)

while running:
    # Lấy vị trí chuột hiện tại mỗi frame để cập nhật hover cho nút
    mouse_pos = pygame.mouse.get_pos()

    # --- Xử lý sự kiện ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            game_state = QUIT # Chuyển trạng thái để thoát

        # Xử lý click chuột
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Xử lý click tùy theo trạng thái game
            if game_state == MENU_MAIN:
                # Lấy rects của nút để kiểm tra click (không cần redraw ở đây)
                # Cần tính lại vị trí nút giống trong draw_main_menu
                button_y_start = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT - 20
                button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
                gap = 20
                button_rects = {
                    'pvp': pygame.Rect(button_x, button_y_start, BUTTON_WIDTH, BUTTON_HEIGHT),
                    'pvai': pygame.Rect(button_x, button_y_start + BUTTON_HEIGHT + gap, BUTTON_WIDTH, BUTTON_HEIGHT)
                }

                if button_rects['pvp'].collidepoint(event.pos):
                    game_mode = 'PvP'
                    game_state = PLAYING # Bắt đầu game PvP
                    # Khởi tạo game mới
                    board = create_board()
                    current_player = PLAYER_X
                    game_over = False
                    winner = None
                    is_menu_open = False # Đảm bảo menu đóng khi bắt đầu game
                    move_history = [] # Xóa lịch sử cũ
                    print("Bắt đầu game 2 người chơi.")
                elif button_rects['pvai'].collidepoint(event.pos):
                    game_state = MENU_DIFFICULTY
                    print("Chuyển sang menu chọn độ khó AI.")

            elif game_state == MENU_DIFFICULTY:
                 # Lấy rects của nút chọn độ khó (không cần redraw)
                 # Cần tính lại vị trí nút giống trong draw_difficulty_menu
                 button_y_start = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT * 1.5 - 2 * 20
                 button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
                 gap = 20
                 button_rects = {
                     'easy': pygame.Rect(button_x, button_y_start, BUTTON_WIDTH, BUTTON_HEIGHT),
                     'medium': pygame.Rect(button_x, button_y_start + BUTTON_HEIGHT + gap, BUTTON_WIDTH, BUTTON_HEIGHT),
                     'hard': pygame.Rect(button_x, button_y_start + 2 * (BUTTON_HEIGHT + gap), BUTTON_WIDTH, BUTTON_HEIGHT),
                     'back': pygame.Rect(20, SCREEN_HEIGHT - BUTTON_HEIGHT - 20, BUTTON_WIDTH/2, BUTTON_HEIGHT/2)
                 }

                 if button_rects['easy'].collidepoint(event.pos):
                     game_mode = 'PvAI'
                     ai_level = DIFFICULTY_EASY
                     ai_search_depth = None
                     game_state = PLAYING
                     # Khởi tạo game mới PvAI
                     board = create_board()
                     current_player = PLAYER_X
                     game_over = False
                     winner = None
                     is_menu_open = False
                     move_history = []
                     is_ai_thinking = False
                     print("Bắt đầu game với máy (Dễ - Heuristic).")
                 elif button_rects['medium'].collidepoint(event.pos):
                     game_mode = 'PvAI'
                     ai_level = DIFFICULTY_MEDIUM
                     ai_search_depth = MEDIUM_DEPTH
                     game_state = PLAYING
                     # Khởi tạo game mới PvAI
                     board = create_board()
                     current_player = PLAYER_X
                     game_over = False
                     winner = None
                     is_menu_open = False
                     move_history = []
                     is_ai_thinking = False
                     print(f"Bắt đầu game với máy (Trung Bình - Minimax Depth={ai_search_depth}).")
                 elif button_rects['hard'].collidepoint(event.pos):
                     game_mode = 'PvAI'
                     ai_level = DIFFICULTY_HARD
                     ai_search_depth = HARD_DEPTH
                     game_state = PLAYING
                     # Khởi tạo game mới PvAI
                     board = create_board()
                     current_player = PLAYER_X
                     game_over = False
                     winner = None
                     is_menu_open = False
                     move_history = []
                     is_ai_thinking = False
                     print(f"Bắt đầu game với máy (Khó - Minimax Depth={ai_search_depth}).")
                 elif button_rects['back'].collidepoint(event.pos):
                      game_state = MENU_MAIN
                      print("Quay lại menu chính.")

            elif game_state == PLAYING:
                 # --- Xử lý click khi đang ở trạng thái PLAYING ---
                 if is_menu_open:
                     # --- Xử lý click khi menu trong game đang mở ---
                     menu_rects = draw_in_game_menu(mouse_pos) # Vẽ và lấy lại rects (không hiển thị ngay)

                     if menu_rects['close'].collidepoint(event.pos):
                         is_menu_open = False # Đóng menu
                         print("Đóng menu trong game.")
                     elif menu_rects['undo'].collidepoint(event.pos):
                         print("Click Undo.")
                         # Xử lý Undo
                         moves_to_undo = 1 if game_mode == 'PvP' else 2
                         undone_count = 0

                         # Lặp để hoàn tác đủ số nước
                         for _ in range(moves_to_undo):
                              if move_history:
                                   last_row, last_col = move_history.pop()
                                   undo_move(board, last_row, last_col)
                                   undone_count += 1
                                   # Đổi lượt chơi ngược lại sau mỗi nước hoàn tác
                                   current_player *= -1
                              else:
                                   break # Không còn nước nào để hoàn tác

                         if undone_count > 0:
                              game_over = False # Nếu hoàn tác, game chưa kết thúc
                              winner = None
                              is_ai_thinking = False # AI cần tính lại nếu lượt của nó bị hoàn tác
                              print(f"Đã hoàn tác {undone_count} nước.")
                         else:
                             print("Không có nước nào để hoàn tác.")

                         is_menu_open = False # Đóng menu sau khi Undo

                     elif menu_rects['restart'].collidepoint(event.pos):
                         print("Click Chơi lại.")
                         # Reset game về trạng thái bắt đầu
                         board = create_board()
                         current_player = PLAYER_X
                         game_over = False
                         winner = None
                         is_menu_open = False
                         move_history = []
                         is_ai_thinking = False
                         # Game mode và AI difficulty vẫn giữ nguyên

                     elif menu_rects['main_menu'].collidepoint(event.pos):
                         print("Click Về Menu Chính.")
                         # Reset game và về menu chính
                         board = None # Đặt board về None hoặc create_board() tùy ý, main menu không cần board
                         current_player = None
                         game_over = False
                         winner = None
                         game_mode = None
                         ai_level = None
                         ai_search_depth = None
                         is_menu_open = False
                         move_history = []
                         is_ai_thinking = False
                         game_state = MENU_MAIN

                     # Click ngoài menu area sẽ đóng menu
                     elif not menu_rects['menu_area'].collidepoint(event.pos):
                         is_menu_open = False
                         print("Click ngoài menu, đóng menu.")

                 else:
                     # --- Xử lý click khi menu trong game đang đóng ---
                     open_button_rect = draw_open_menu_button(mouse_pos) # Vẽ và lấy rect (không hiển thị ngay)
                     if open_button_rect.collidepoint(event.pos):
                         is_menu_open = True # Mở menu
                         print("Mở menu trong game.")
                     elif not game_over and not is_ai_thinking: # Chỉ xử lý click bàn cờ khi game chưa kết thúc và AI không nghĩ
                         pos = event.pos
                         row, col = get_row_col_from_mouse(pos)

                         if row is not None and col is not None and is_valid_location(board, row, col):
                              if game_mode == 'PvP':
                                  if place_piece(board, row, col, current_player):
                                      move_history.append((row, col)) # Lưu nước đi
                                      if check_win(board, current_player):
                                          winner = current_player
                                          game_over = True
                                          game_state = GAME_OVER
                                      elif check_draw(board):
                                          winner = 'Draw'
                                          game_over = True
                                          game_state = GAME_OVER
                                      else:
                                          current_player *= -1

                              elif game_mode == 'PvAI' and current_player == HUMAN_PLAYER:
                                  if place_piece(board, row, col, HUMAN_PLAYER):
                                      move_history.append((row, col)) # Lưu nước đi
                                      if check_win(board, HUMAN_PLAYER):
                                          winner = HUMAN_PLAYER
                                          game_over = True
                                          game_state = GAME_OVER
                                      elif check_draw(board):
                                          winner = 'Draw'
                                          game_over = True
                                          game_state = GAME_OVER
                                      else:
                                          current_player = AI_PLAYER
                                          is_ai_thinking = True # Bắt đầu trạng thái AI nghĩ


    # --- Cập nhật và Vẽ màn hình dựa trên trạng thái game ---

    if game_state == MENU_MAIN:
        draw_main_menu(mouse_pos)

    elif game_state == MENU_DIFFICULTY:
        draw_difficulty_menu(mouse_pos)

    elif game_state == PLAYING:
        draw_board(board)
        draw_turn_message(current_player, game_mode, is_ai_thinking)
        draw_open_menu_button(mouse_pos) # Luôn vẽ nút mở menu khi đang chơi

        # Nếu menu đang mở, vẽ menu lên trên cùng
        if is_menu_open:
            draw_in_game_menu(mouse_pos) # Vẽ menu overlay

        # Xử lý lượt đi của AI (chỉ trong chế độ PvAI và khi đến lượt AI)
        # Kiểm tra is_ai_thinking để đảm bảo chỉ gọi get_ai_move một lần mỗi lượt AI
        # AI không đánh khi menu đang mở
        if game_mode == 'PvAI' and current_player == AI_PLAYER and not game_over and is_ai_thinking and not is_menu_open:
            # AI đang nghĩ, hiển thị thông báo (đã làm trong draw_turn_message)
            # Bây giờ thực hiện tính toán của AI
            ai_row, ai_col = get_ai_move(board, ai_level, ai_search_depth)

            if ai_row is not None and ai_col is not None:
                 # Kiểm tra lại lần nữa nước đi có hợp lệ trên bàn cờ hiện tại không
                 if is_valid_location(board, ai_row, ai_col):
                     place_piece(board, ai_row, ai_col, AI_PLAYER)
                     move_history.append((ai_row, ai_col)) # Lưu nước đi của AI

                     if check_win(board, AI_PLAYER):
                         winner = AI_PLAYER
                         game_over = True
                         game_state = GAME_OVER
                     elif check_draw(board):
                         winner = 'Draw'
                         game_over = True
                         game_state = GAME_OVER
                     else:
                         current_player = HUMAN_PLAYER # Đổi lượt lại cho người
                 else:
                     # Trường hợp AI trả về nước không hợp lệ
                     print(f"Lỗi AI: Trả về nước không hợp lệ ({ai_row}, {ai_col})")
                     game_over = True
                     winner = 'Lỗi AI'
                     game_state = GAME_OVER

                 is_ai_thinking = False # Kết thúc trạng thái AI nghĩ
            else:
                 # Trường hợp AI không tìm được nước đi hợp lệ (ví dụ bàn cờ đầy)
                 print("AI không tìm được nước đi hợp lệ.")
                 game_over = True
                 winner = 'Lỗi AI?' # Hoặc 'Hòa' tùy tình huống
                 game_state = GAME_OVER
                 is_ai_thinking = False # Kết thúc trạng thái AI nghĩ


    elif game_state == GAME_OVER:
        draw_board(board)
        message = ""
        if winner == PLAYER_X:
            message = "Người chơi X thắng!"
        elif winner == PLAYER_O:
             message = "Người chơi O (Máy) thắng!"
        elif winner == 'Draw':
            message = "Hòa!"
        else:
             message = "Kết thúc game." # Trường hợp khác (ví dụ Lỗi AI)

        draw_message(message, color=RED)
        draw_message("Click để về Menu", color=BLACK, center_y = SCREEN_HEIGHT - GUI_MARGIN // 2)

        # Vòng lặp chờ click để quay về menu
        waiting_for_click = True
        while waiting_for_click:
             for event in pygame.event.get():
                 if event.type == pygame.QUIT:
                     running = False
                     game_state = QUIT
                     waiting_for_click = False
                 if event.type == pygame.MOUSEBUTTONDOWN:
                     game_state = MENU_MAIN # Quay về menu
                     waiting_for_click = False
                     # Reset trạng thái game khi về menu chính
                     board = None
                     current_player = None
                     game_over = False
                     winner = None
                     game_mode = None
                     ai_level = None
                     ai_search_depth = None
                     is_menu_open = False
                     move_history = []
                     is_ai_thinking = False

             # Cần cập nhật màn hình trong vòng lặp chờ này
             pygame.display.flip()


    # Cập nhật toàn bộ màn hình (trừ khi đang trong vòng lặp chờ của GAME_OVER)
    # pygame.display.flip() được gọi riêng trong vòng lặp chờ GAME_OVER
    if game_state != GAME_OVER:
       pygame.display.flip()


# Thoát Pygame khi running = False và game_state = QUIT
if game_state == QUIT:
    quit_pygame()