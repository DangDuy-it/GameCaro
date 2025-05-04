# graphics.py
import pygame
import sys
# Import tường minh các hằng số cần thiết từ constants.py
from constants import (
    BOARD_SIZE, CELL_SIZE, GUI_MARGIN, SCREEN_WIDTH, SCREEN_HEIGHT,
    LINE_THICKNESS, PIECE_SIZE,
    WHITE, BLACK, RED, GREEN, BLUE, BOARD_COLOR, # Thêm BLUE cho nút menu
    PLAYER_X, PLAYER_O, AI_PLAYER, HUMAN_PLAYER,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    INGAME_MENU_WIDTH, INGAME_MENU_HEIGHT, INGAME_MENU_COLOR, INGAME_MENU_BORDER_COLOR,
    INGAME_MENU_BUTTON_WIDTH, INGAME_MENU_BUTTON_HEIGHT, INGAME_MENU_BUTTON_GAP,
    MENU_BUTTON_SIZE, MENU_BUTTON_MARGIN
)

# Khởi tạo Pygame và các đối tượng vẽ
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Caro V.I.P")

# Fonts (truy cập qua hàm get_)
_font = pygame.font.SysFont("monospace", 40)
_small_font = pygame.font.SysFont("monospace", 25)
_button_font = pygame.font.SysFont("monospace", 30) # Font cho nút menu chính
_ingame_button_font = pygame.font.SysFont("monospace", 25) # Font cho nút trong game menu

def get_screen(): return screen
def get_font(): return _font
def get_small_font(): return _small_font
def get_button_font(): return _button_font
def get_ingame_button_font(): return _ingame_button_font # Thêm hàm lấy font nút trong game

# ... (Giữ nguyên các hàm draw_board, get_row_col_from_mouse, draw_message, draw_turn_message)

def draw_board(board):
    """Vẽ bàn cờ và các quân cờ lên màn hình."""
    screen.fill(BOARD_COLOR) # Tô màu nền bàn cờ

    # Vẽ lưới
    for row in range(BOARD_SIZE):
        # Vẽ hàng ngang
        pygame.draw.line(screen, BLACK,
                         (GUI_MARGIN, GUI_MARGIN + row * CELL_SIZE),
                         (GUI_MARGIN + BOARD_SIZE * CELL_SIZE, GUI_MARGIN + row * CELL_SIZE),
                         LINE_THICKNESS)
        # Vẽ cột dọc
        pygame.draw.line(screen, BLACK,
                         (GUI_MARGIN + row * CELL_SIZE, GUI_MARGIN),
                         (GUI_MARGIN + row * CELL_SIZE, GUI_MARGIN + BOARD_SIZE * CELL_SIZE),
                         LINE_THICKNESS)

    # Vẽ các quân cờ
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            center_x = GUI_MARGIN + col * CELL_SIZE + CELL_SIZE // 2
            center_y = GUI_MARGIN + row * CELL_SIZE + CELL_SIZE // 2
            if board[row][col] == PLAYER_X:
                # Vẽ quân cờ X (hai đường chéo)
                pygame.draw.line(screen, BLACK,
                                 (center_x - PIECE_SIZE, center_y - PIECE_SIZE),
                                 (center_x + PIECE_SIZE, center_y + PIECE_SIZE),
                                 3)
                pygame.draw.line(screen, BLACK,
                                 (center_x + PIECE_SIZE, center_y - PIECE_SIZE),
                                 (center_x - PIECE_SIZE, center_y + PIECE_SIZE),
                                 3)
            elif board[row][col] == PLAYER_O:
                # Vẽ quân cờ O (hình tròn)
                pygame.draw.circle(screen, BLACK, (center_x, center_y), PIECE_SIZE, 3)

def get_row_col_from_mouse(pos):
    """Chuyển đổi vị trí click chuột (pixel) sang chỉ số hàng, cột trên bàn cờ."""
    mouse_x, mouse_y = pos
    if GUI_MARGIN <= mouse_x <= GUI_MARGIN + BOARD_SIZE * CELL_SIZE and \
       GUI_MARGIN <= mouse_y <= GUI_MARGIN + BOARD_SIZE * CELL_SIZE:
        col = (mouse_x - GUI_MARGIN) // CELL_SIZE
        row = (mouse_y - GUI_MARGIN) // CELL_SIZE
        # Đảm bảo chỉ số nằm trong giới hạn
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
             return row, col
    return None, None # Click ngoài bàn cờ hoặc ngoài bàn cờ logic

def draw_message(message, color=RED, center_y=GUI_MARGIN // 2):
    """Hiển thị thông báo lên màn hình."""
    label = get_font().render(message, 1, color)
    # Hiển thị ở giữa phía trên hoặc vị trí tùy chỉnh
    screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, center_y - label.get_height() // 2))
    # Không cần update/wait ở đây, sẽ update chung trong main loop

def draw_turn_message(current_player, game_mode, is_ai_thinking=False):
    """Hiển thị thông báo lượt chơi."""
    turn_message = "Lượt của: "
    if current_player == PLAYER_X:
        turn_message += "X" if game_mode == 'PvP' else "Người chơi (X)"
    elif current_player == PLAYER_O:
         turn_message += "O" if game_mode == 'PvP' else "Máy (O)"

    turn_label = get_small_font().render(turn_message, 1, BLACK)
    screen.blit(turn_label, (GUI_MARGIN, GUI_MARGIN // 4)) # Hiển thị ở góc trên trái

    if game_mode == 'PvAI' and current_player == AI_PLAYER and is_ai_thinking:
        thinking_label = get_small_font().render("Máy đang nghĩ...", 1, BLACK)
        screen.blit(thinking_label, (SCREEN_WIDTH - GUI_MARGIN - thinking_label.get_width(), GUI_MARGIN // 4))

# Hàm vẽ nút chung (đã có, nhưng đảm bảo dùng font đúng)
def draw_button(text, rect, mouse_pos, font_renderer):
    """Vẽ một nút và kiểm tra xem chuột có hover qua không. Trả về Rect của nút."""
    color = BUTTON_COLOR
    if rect.collidepoint(mouse_pos):
        color = BUTTON_HOVER_COLOR

    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2) # Viền nút

    label = font_renderer.render(text, 1, BUTTON_TEXT_COLOR)
    text_rect = label.get_rect(center=rect.center)
    screen.blit(label, text_rect)

    return rect # Trả về hình chữ nhật của nút để kiểm tra click trong main loop


# Cập nhật hàm vẽ menu chính để dùng font đúng
def draw_main_menu(mouse_pos):
    """Vẽ màn hình menu chính."""
    screen.fill(WHITE)
    title = get_font().render("Game Caro V.I.P", 1, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    # Tính vị trí các nút
    button_y_start = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT - 20
    button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
    gap = 20

    pvp_button_rect = pygame.Rect(button_x, button_y_start, BUTTON_WIDTH, BUTTON_HEIGHT)
    pvai_button_rect = pygame.Rect(button_x, button_y_start + BUTTON_HEIGHT + gap, BUTTON_WIDTH, BUTTON_HEIGHT)

    # Vẽ nút và lấy lại rect để kiểm tra click, dùng font nút menu chính
    pvp_rect = draw_button("2 Người Chơi", pvp_button_rect, mouse_pos, get_button_font())
    pvai_rect = draw_button("Chơi với Máy", pvai_button_rect, mouse_pos, get_button_font())

    return {'pvp': pvp_rect, 'pvai': pvai_rect}

# Cập nhật hàm vẽ menu độ khó để dùng font đúng
def draw_difficulty_menu(mouse_pos):
    """Vẽ màn hình chọn độ khó AI."""
    screen.fill(WHITE)
    title = get_font().render("Chọn Độ Khó AI", 1, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    # Tính vị trí các nút
    button_y_start = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT * 1.5 - 2 * 20
    button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
    gap = 20

    easy_button_rect = pygame.Rect(button_x, button_y_start, BUTTON_WIDTH, BUTTON_HEIGHT)
    medium_button_rect = pygame.Rect(button_x, button_y_start + BUTTON_HEIGHT + gap, BUTTON_WIDTH, BUTTON_HEIGHT)
    hard_button_rect = pygame.Rect(button_x, button_y_start + 2 * (BUTTON_HEIGHT + gap), BUTTON_WIDTH, BUTTON_HEIGHT)
    back_button_rect = pygame.Rect(20, SCREEN_HEIGHT - BUTTON_HEIGHT - 20, BUTTON_WIDTH/2, BUTTON_HEIGHT/2) # Nút quay lại nhỏ

    # Vẽ nút và lấy lại rect để kiểm tra click, dùng font nút menu chính
    easy_rect = draw_button("Dễ", easy_button_rect, mouse_pos, get_button_font())
    medium_rect = draw_button("Trung Bình", medium_button_rect, mouse_pos, get_button_font())
    hard_rect = draw_button("Khó", hard_button_rect, mouse_pos, get_button_font())
    back_rect = draw_button("Trở lại", back_button_rect, mouse_pos, get_small_font()) # Dùng font nhỏ hơn cho nút back

    return {'easy': easy_rect, 'medium': medium_rect, 'hard': hard_rect, 'back': back_rect}


# --- Thêm hàm vẽ nút mở menu trong game ---
def draw_open_menu_button(mouse_pos):
    """Vẽ nút nhỏ để mở menu trong game."""
    rect = pygame.Rect(SCREEN_WIDTH - MENU_BUTTON_SIZE - MENU_BUTTON_MARGIN,
                       MENU_BUTTON_MARGIN,
                       MENU_BUTTON_SIZE,
                       MENU_BUTTON_SIZE)
    # Dùng màu khác cho nút này
    color = BLUE
    if rect.collidepoint(mouse_pos):
         color = (0, 0, 200) # Màu xanh đậm hơn khi hover

    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

    # Vẽ 3 gạch ngang đơn giản như biểu tượng menu
    line_y_start = rect.centery - 6
    line_height = 3
    line_x_margin = 8
    pygame.draw.line(screen, WHITE, (rect.left + line_x_margin, line_y_start), (rect.right - line_x_margin, line_y_start), line_height)
    pygame.draw.line(screen, WHITE, (rect.left + line_x_margin, rect.centery), (rect.right - line_x_margin, rect.centery), line_height)
    pygame.draw.line(screen, WHITE, (rect.left + line_x_margin, rect.centery + 6), (rect.right - line_x_margin, rect.centery + 6), line_height)


    return rect # Trả về rect để xử lý click


# --- Thêm hàm vẽ menu trong game ---
def draw_in_game_menu(mouse_pos):
    """Vẽ menu overlay khi đang trong game."""
    menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - INGAME_MENU_WIDTH // 2,
                            SCREEN_HEIGHT // 2 - INGAME_MENU_HEIGHT // 2,
                            INGAME_MENU_WIDTH,
                            INGAME_MENU_HEIGHT)

    # Vẽ nền và viền menu
    pygame.draw.rect(screen, INGAME_MENU_COLOR, menu_rect)
    pygame.draw.rect(screen, INGAME_MENU_BORDER_COLOR, menu_rect, 3)

    # Tính vị trí các nút trong menu
    button_x = menu_rect.centerx - INGAME_MENU_BUTTON_WIDTH // 2
    button_y_start = menu_rect.top + 40 # Khoảng cách từ đỉnh menu

    gap = INGAME_MENU_BUTTON_GAP

    undo_rect_pos = pygame.Rect(button_x, button_y_start, INGAME_MENU_BUTTON_WIDTH, INGAME_MENU_BUTTON_HEIGHT)
    restart_rect_pos = pygame.Rect(button_x, button_y_start + INGAME_MENU_BUTTON_HEIGHT + gap, INGAME_MENU_BUTTON_WIDTH, INGAME_MENU_BUTTON_HEIGHT)
    main_menu_rect_pos = pygame.Rect(button_x, button_y_start + 2 * (INGAME_MENU_BUTTON_HEIGHT + gap), INGAME_MENU_BUTTON_WIDTH, INGAME_MENU_BUTTON_HEIGHT)
    close_rect_pos = pygame.Rect(menu_rect.right - 30, menu_rect.top + 10, 20, 20) # Nút X đóng menu nhỏ

    # Vẽ các nút và lấy lại rects để xử lý click, dùng font nút trong game
    undo_rect = draw_button("Quay lại (Undo)", undo_rect_pos, mouse_pos, get_ingame_button_font())
    restart_rect = draw_button("Chơi lại", restart_rect_pos, mouse_pos, get_ingame_button_font())
    main_menu_rect = draw_button("Về Menu Chính", main_menu_rect_pos, mouse_pos, get_ingame_button_font())

    # Vẽ nút đóng menu (biểu tượng X)
    pygame.draw.rect(screen, RED, close_rect_pos) # Nền đỏ
    pygame.draw.rect(screen, BLACK, close_rect_pos, 2) # Viền đen
    pygame.draw.line(screen, BLACK, (close_rect_pos.left + 4, close_rect_pos.top + 4), (close_rect_pos.right - 4, close_rect_pos.bottom - 4), 2)
    pygame.draw.line(screen, BLACK, (close_rect_pos.right - 4, close_rect_pos.top + 4), (close_rect_pos.left + 4, close_rect_pos.bottom - 4), 2)
    close_rect = close_rect_pos # Trả về rect để xử lý click


    return {'undo': undo_rect, 'restart': restart_rect, 'main_menu': main_menu_rect, 'close': close_rect, 'menu_area': menu_rect}


def quit_pygame():
    """Thoát Pygame."""
    pygame.quit()
    sys.exit()