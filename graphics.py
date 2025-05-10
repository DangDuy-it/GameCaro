# graphics.py
import pygame
import sys
# Import tường minh các hằng số cần thiết từ constants.py
from constants import (
    BOARD_SIZE, CELL_SIZE, GUI_MARGIN, SCREEN_WIDTH, SCREEN_HEIGHT,
    LINE_THICKNESS,
    WHITE, BLACK, RED, GREEN, BLUE, BOARD_COLOR,
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
def get_ingame_button_font(): return _ingame_button_font

# --- Tải và lưu trữ hình ảnh (Thêm mới/Cập nhật) ---
# Biến toàn cục để lưu trữ ảnh
background_fullscreen_img = None # <-- Biến mới cho ảnh nền toàn màn hình
board_background_img = None
x_piece_img = None
o_piece_img = None
# ... (các biến ảnh win/lose/start nếu có)

try:
    # --- Tải ảnh nền toàn màn hình (Thêm mới) ---
    # Hãy thay đổi 'images/background.png' nếu tên file ảnh nền toàn màn hình của bạn khác
    # Nếu bạn không có ảnh nền toàn màn hình riêng, có thể dùng lại board.png và scale lớn,
    # nhưng lưu ý có thể bị biến dạng nếu tỷ lệ ảnh không khớp màn hình.
    try:
         background_fullscreen_img = pygame.image.load('images/background.png').convert_alpha()
         background_fullscreen_img = pygame.transform.scale(background_fullscreen_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
         print("Warning: 'images/background.png' not found. Using WHITE background.")
         background_fullscreen_img = None # Set None nếu không tải được


    # Tải ảnh background bàn cờ (vẫn dùng cho khu vực bàn cờ cụ thể)
    board_background_img = pygame.image.load('images/board.png').convert_alpha()
    board_render_size = BOARD_SIZE * CELL_SIZE
    board_background_img = pygame.transform.scale(board_background_img, (board_render_size, board_render_size))

    # Tải ảnh quân cờ
    x_piece_img = pygame.image.load('images/X.png').convert_alpha()
    o_piece_img = pygame.image.load('images/O.png').convert_alpha()

    # Scale ảnh quân cờ
    piece_display_size = CELL_SIZE - 4
    x_piece_img = pygame.transform.scale(x_piece_img, (piece_display_size, piece_display_size))
    o_piece_img = pygame.transform.scale(o_piece_img, (piece_display_size, piece_display_size))

    # ... (Tải thêm ảnh khác nếu có, ví dụ win.png, lose.png)

except pygame.error as e:
    print(f"Không thể tải một số hình ảnh quan trọng (board.png, X.png, O.png): {e}")
    print("Hãy đảm bảo thư mục 'images' tồn tại và chứa các file ảnh cần thiết.")
    pygame.quit()
    sys.exit()


# --- Cập nhật các hàm vẽ để dùng ảnh nền toàn màn hình ---

# Hàm vẽ bàn cờ (draw_board) giờ sẽ vẽ ảnh nền toàn màn hình trước
def draw_board(board):
    """Vẽ bàn cờ và các quân cờ lên màn hình sử dụng ảnh."""
    # 1. Vẽ ảnh nền toàn màn hình ĐẦU TIÊN (nếu có), nếu không thì tô màu trắng
    if background_fullscreen_img:
        screen.blit(background_fullscreen_img, (0, 0))
    else:
        screen.fill(WHITE) # Fallback nếu không có ảnh nền toàn màn hình


    # 2. Vẽ ảnh bàn cờ tại vị trí bàn cờ (bao gồm cả lề GUI_MARGIN), NẰM TRÊN ảnh nền toàn màn hình
    # Đảm bảo board_background_img đã tải thành công (đã có try/except lớn ở trên)
    screen.blit(board_background_img, (GUI_MARGIN, GUI_MARGIN))


    # 3. Vẽ lưới (Chỉ vẽ nếu ảnh board.png không có lưới, hoặc bạn muốn vẽ lưới sắc nét hơn lên trên ảnh)
    # >>> THỬ BỎ COMMENT (HOẶC XÓA) TOÀN BỘ KHỐI CODE NÀY NẾU ẢNH board.png ĐÃ CÓ LƯỚI <<<
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
    # --- Kết thúc phần vẽ lưới Pygame ---


    # 4. Vẽ các quân cờ sử dụng ảnh (Giữ nguyên logic này)
    # Đảm bảo các biến x_piece_img, o_piece_img đã được tải thành công
    if x_piece_img and o_piece_img:
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Tính toán vị trí góc trên trái để vẽ ảnh quân cờ bên trong ô
                piece_x = GUI_MARGIN + col * CELL_SIZE + (CELL_SIZE - piece_display_size) // 2
                piece_y = GUI_MARGIN + row * CELL_SIZE + (CELL_SIZE - piece_display_size) // 2

                if board[row][col] == PLAYER_X:
                    screen.blit(x_piece_img, (piece_x, piece_y))
                elif board[row][col] == PLAYER_O:
                    screen.blit(o_piece_img, (piece_x, piece_y))
    else:
        # Fallback: Nếu ảnh không tải được, vẽ quân cờ bằng hình khối như cũ
        print("Warning: Drawing pieces with shapes as images failed to load.")
        current_piece_size = CELL_SIZE // 2 - 2
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                center_x = GUI_MARGIN + col * CELL_SIZE + CELL_SIZE // 2
                center_y = GUI_MARGIN + row * CELL_SIZE + CELL_SIZE // 2
                # PIECE_SIZE có thể không được import nếu bỏ dùng
                current_piece_size = CELL_SIZE // 2 - 2 # Tính lại kích thước nếu PIECE_SIZE không tồn tại
                if board[row][col] == PLAYER_X:
                    pygame.draw.line(screen, BLACK,
                                     (center_x - current_piece_size, center_y - current_piece_size),
                                     (center_x + current_piece_size, center_y + current_piece_size), 3)
                    pygame.draw.line(screen, BLACK,
                                     (center_x + current_piece_size, center_y - current_piece_size),
                                     (center_x - current_piece_size, center_y + current_piece_size), 3)
                elif board[row][col] == PLAYER_O:
                    pygame.draw.circle(screen, BLACK, (center_x, center_y), current_piece_size, 3)


# Hàm vẽ menu chính (draw_main_menu) giờ sẽ vẽ ảnh nền toàn màn hình trước
def draw_main_menu(mouse_pos):
    """Vẽ màn hình menu chính."""
    # Vẽ ảnh nền toàn màn hình ĐẦU TIÊN (nếu có), nếu không thì tô màu trắng
    if background_fullscreen_img:
        screen.blit(background_fullscreen_img, (0, 0))
    else:
        screen.fill(WHITE) # Fallback

    # ... (Vẽ tiêu đề, các nút, v.v. lên trên ảnh nền) ...
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

    # Có thể thêm ảnh start.png ở đây nếu muốn
    # if 'start_img' in globals() and start_img:
    #     start_rect = start_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150)) # Vị trí ví dụ
    #     screen.blit(start_img, start_rect)


    return {'pvp': pvp_rect, 'pvai': pvai_rect}

# Hàm vẽ menu độ khó (draw_difficulty_menu) giờ sẽ vẽ ảnh nền toàn màn hình trước
def draw_difficulty_menu(mouse_pos):
    """Vẽ màn hình chọn độ khó AI."""
    # Vẽ ảnh nền toàn màn hình ĐẦU TIÊN (nếu có), nếu không thì tô màu trắng
    if background_fullscreen_img:
        screen.blit(background_fullscreen_img, (0, 0))
    else:
        screen.fill(WHITE) # Fallback

    # ... (Vẽ tiêu đề, các nút, v.v. lên trên ảnh nền) ...
    title = get_font().render("Chọn Độ Khó AI", 1, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    # Tính vị trí các nút
    button_y_start = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT * 1.5 - 2 * 20
    button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
    gap = 20

    easy_button_rect = pygame.Rect(button_x, button_y_start, BUTTON_WIDTH, BUTTON_HEIGHT)
    medium_button_rect = pygame.Rect(button_x, button_y_start + BUTTON_HEIGHT + gap, BUTTON_WIDTH, BUTTON_HEIGHT)
    hard_button_rect = pygame.Rect(button_x, button_y_start + 2 * (BUTTON_HEIGHT + gap), BUTTON_WIDTH, INGAME_MENU_BUTTON_HEIGHT) # Sửa lỗi copy-paste: dùng BUTTON_HEIGHT
    back_button_rect = pygame.Rect(20, SCREEN_HEIGHT - BUTTON_HEIGHT - 20, BUTTON_WIDTH/2, BUTTON_HEIGHT/2) # Nút quay lại nhỏ

    # Vẽ nút và lấy lại rect để kiểm tra click, dùng font nút menu chính
    easy_rect = draw_button("Dễ", easy_button_rect, mouse_pos, get_button_font())
    medium_rect = draw_button("Trung Bình", medium_button_rect, mouse_pos, get_button_font())
    hard_rect = draw_button("Khó", hard_button_rect, mouse_pos, get_button_font())
    back_rect = draw_button("Trở lại", back_button_rect, mouse_pos, get_small_font()) # Dùng font nhỏ hơn cho nút back

    return {'easy': easy_rect, 'medium': medium_rect, 'hard': hard_rect, 'back': back_rect}


# draw_game_over_screen gọi draw_board, nên nó sẽ có background toàn màn hình

# ... (Các hàm vẽ khác giữ nguyên) ...

def get_row_col_from_mouse(pos):
    # ... (giữ nguyên)
     mouse_x, mouse_y = pos
     if GUI_MARGIN <= mouse_x <= GUI_MARGIN + BOARD_SIZE * CELL_SIZE and \
        GUI_MARGIN <= mouse_y <= GUI_MARGIN + BOARD_SIZE * CELL_SIZE:
         col = (mouse_x - GUI_MARGIN) // CELL_SIZE
         row = (mouse_y - GUI_MARGIN) // CELL_SIZE
         # Đảm bảo chỉ số nằm trong giới hạn
         if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
              return row, col
     return None, None


def draw_message(message, color=RED, center_y=GUI_MARGIN // 2):
    # ... (giữ nguyên)
    label = get_font().render(message, 1, color)
    screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, center_y - label.get_height() // 2))


def draw_turn_message(current_player, game_mode, is_ai_thinking=False):
    # ... (giữ nguyên)
     turn_message = "Lượt của: "
     if current_player == PLAYER_X:
         turn_message += "X" if game_mode == 'PvP' else "Người chơi (X)"
     elif current_player == PLAYER_O:
          turn_message += "O" if game_mode == 'PvP' else "Máy (O)"

     turn_label = get_small_font().render(turn_message, 1, BLACK)
     screen.blit(turn_label, (GUI_MARGIN, GUI_MARGIN // 4))

     if game_mode == 'PvAI' and current_player == AI_PLAYER and is_ai_thinking:
         thinking_label = get_small_font().render("Máy đang nghĩ...", 1, BLACK)
         screen.blit(thinking_label, (SCREEN_WIDTH - GUI_MARGIN - thinking_label.get_width(), GUI_MARGIN // 4))


def draw_button(text, rect, mouse_pos, font_renderer):
    # ... (giữ nguyên)
     color = BUTTON_COLOR
     if rect.collidepoint(mouse_pos):
         color = BUTTON_HOVER_COLOR

     pygame.draw.rect(screen, color, rect)
     pygame.draw.rect(screen, BLACK, rect, 2)

     label = font_renderer.render(text, 1, BUTTON_TEXT_COLOR)
     text_rect = label.get_rect(center=rect.center)
     screen.blit(label, text_rect)

     return rect


def draw_open_menu_button(mouse_pos):
    # ... (giữ nguyên)
     rect = pygame.Rect(SCREEN_WIDTH - MENU_BUTTON_SIZE - MENU_BUTTON_MARGIN,
                        MENU_BUTTON_MARGIN,
                        MENU_BUTTON_SIZE,
                        MENU_BUTTON_SIZE)
     color = BLUE
     if rect.collidepoint(mouse_pos):
          color = (0, 0, 200)

     pygame.draw.rect(screen, color, rect)
     pygame.draw.rect(screen, BLACK, rect, 2)

     line_y_start = rect.centery - 6
     line_height = 3
     line_x_margin = 8
     pygame.draw.line(screen, WHITE, (rect.left + line_x_margin, line_y_start), (rect.right - line_x_margin, line_y_start), line_height)
     pygame.draw.line(screen, WHITE, (rect.left + line_x_margin, rect.centery), (rect.right - line_x_margin, rect.centery), line_height)
     pygame.draw.line(screen, WHITE, (rect.left + line_x_margin, rect.centery + 6), (rect.right - line_x_margin, rect.centery + 6), line_height)

     return rect


def draw_in_game_menu(mouse_pos):
    # ... (giữ nguyên)
     menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - INGAME_MENU_WIDTH // 2,
                             SCREEN_HEIGHT // 2 - INGAME_MENU_HEIGHT // 2,
                             INGAME_MENU_WIDTH,
                             INGAME_MENU_HEIGHT)

     pygame.draw.rect(screen, INGAME_MENU_COLOR, menu_rect)
     pygame.draw.rect(screen, INGAME_MENU_BORDER_COLOR, menu_rect, 3)

     button_x = menu_rect.centerx - INGAME_MENU_BUTTON_WIDTH // 2
     button_y_start = menu_rect.top + 40

     gap = INGAME_MENU_BUTTON_GAP

     undo_rect_pos = pygame.Rect(button_x, button_y_start, INGAME_MENU_BUTTON_WIDTH, INGAME_MENU_BUTTON_HEIGHT)
     restart_rect_pos = pygame.Rect(button_x, button_y_start + INGAME_MENU_BUTTON_HEIGHT + gap, INGAME_MENU_BUTTON_WIDTH, INGAME_MENU_BUTTON_HEIGHT)
     main_menu_rect_pos = pygame.Rect(button_x, button_y_start + 2 * (INGAME_MENU_BUTTON_HEIGHT + gap), INGAME_MENU_BUTTON_WIDTH, INGAME_MENU_BUTTON_HEIGHT)
     close_rect_pos = pygame.Rect(menu_rect.right - 30, menu_rect.top + 10, 20, 20)

     undo_rect = draw_button("Quay lại", undo_rect_pos, mouse_pos, get_ingame_button_font())
     restart_rect = draw_button("Chơi lại", restart_rect_pos, mouse_pos, get_ingame_button_font())
     main_menu_rect = draw_button("Về Menu Chính", main_menu_rect_pos, mouse_pos, get_ingame_button_font())

     pygame.draw.rect(screen, RED, close_rect_pos)
     pygame.draw.rect(screen, BLACK, close_rect_pos, 2)
     pygame.draw.line(screen, BLACK, (close_rect_pos.left + 4, close_rect_pos.top + 4), (close_rect_pos.right - 4, close_rect_pos.bottom - 4), 2)
     pygame.draw.line(screen, BLACK, (close_rect_pos.right - 4, close_rect_pos.top + 4), (close_rect_pos.left + 4, close_rect_pos.bottom - 4), 2)
     close_rect = close_rect_pos

     return {'undo': undo_rect, 'restart': restart_rect, 'main_menu': main_menu_rect, 'close': close_rect, 'menu_area': menu_rect}


def draw_game_over_screen(winner_type, board):
    """Vẽ màn hình kết thúc game, có thể dùng ảnh win/lose."""
    # Vẽ lại bàn cờ lần cuối (draw_board đã có background toàn màn hình)
    draw_board(board)

    # ... (Tùy chọn sử dụng ảnh win/lose nếu có) ...

    message = ""
    if winner_type == PLAYER_X:
        message = "Người chơi X thắng!"
    elif winner_type == PLAYER_O:
        message = "Người chơi O (Máy) thắng!"
    elif winner_type == 'Draw':
        message = "Hòa!"
    else:
        message = "Kết thúc game."

    # Vẫn dùng draw_message để hiển thị kết quả và thông báo click về menu
    draw_message(message, color=RED, center_y=SCREEN_HEIGHT // 2 - 50)
    draw_message("Click để về Menu", color=BLACK, center_y = SCREEN_HEIGHT - GUI_MARGIN // 2)


def quit_pygame():
    """Thoát Pygame."""
    pygame.quit()
    sys.exit()