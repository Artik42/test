import pygame
import random
import os

# Ініціалізація всіх імпортованих модулів pygame
pygame.init()
pygame.mixer.init()

# Налаштування розмірів вікна та створення головної поверхні (екрана)
w, h = 800, 600
screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("cross dot") # Встановлення заголовка вікна гри
clock = pygame.time.Clock() # Створення таймера для контролю частоти кадрів (FPS)

# Завантаження шрифтів для звичайного та великого тексту
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 48)

# Допоміжна функція для отримання правильного шляху до файлів ресурсів (аудіо тощо)
def path(fils):
    return os.path.join(os.path.dirname(__file__), fils)

# Завантаження фонової музики, якщо файл існує; інакше — обробка винятку (гра не вилетить)
try:
    pygame.mixer.music.load(path("fon.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1) # Запуск музики циклічно (-1)
except Exception:
    pass

# Завантаження звуку перемоги, якщо файл існує
try:
    win_sound = pygame.mixer.Sound(path("win.mp3"))
except Exception:
    win_sound = None

sound_enabled = True # Прапорець увімкнення/вимкнення звуку

# Визначення кольорів у форматі RGB
BG_COLOR = (30, 30, 40)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (70, 130, 180)
RED = (220, 80, 80)
GREEN = (80, 180, 80)

# Ігрові стани: головне меню, вибір складності, гра, пауза, кінець гри
game_state = 'MENU'
difficulty = 'easy' # Початкова складність: 'easy' (3x3), 'medium' (8x8), 'hard' (12x12)

# Функція налаштування дошки залежно від обраної складності
def setup_board(diff):
    if diff == 'easy':
        return 3, 3, 3 # розмір дошки, довжина серії для перемоги, розмір сітки
    elif diff == 'medium':
        return 8, 4, 8
    else:
        return 12, 6, 12

# Початкові параметри дошки
grid_size, win_streak, board_dim = 3, 3, 3
# Створення двовимірного масиву (сітки) для ігрового поля, заповненого значеннями None
board = [[None for _ in range(board_dim)] for _ in range(board_dim)]
current_player = 'X' # 'X' — гравець, 'O' — штучний інтелект (комп'ютер)
winner = None # Змінна для збереження переможця
winning_cells = [] # Список виграшних клітинок для їх підсвічування

# Кнопки для Головного меню (розташування та розміри: x, y, ширина, висота)
play_button = pygame.Rect(300, 260, 200, 60)
exit_button = pygame.Rect(300, 340, 200, 60)

# Кнопки вибору складності
diff_easy_btn = pygame.Rect(250, 200, 300, 50)
diff_med_btn = pygame.Rect(250, 270, 300, 50)
diff_hard_btn = pygame.Rect(250, 340, 300, 50)

# Кнопки керування всередині гри (панель праворуч)
reset_btn = pygame.Rect(620, 100, 150, 40)
pause_btn = pygame.Rect(620, 160, 150, 40)
sound_btn = pygame.Rect(620, 220, 150, 40)
menu_btn = pygame.Rect(620, 280, 150, 40)

# Функція перевірки виграшу або нічиєї на дошці
def check_win(b, size, streak):
    # Перевірка рядків, стовпчиків та діагоналей на наявність виграшної серії
    for r in range(size):
        for c in range(size):
            if b[r][c] is None:
                continue
            player = b[r][c]
            
            # Перевірка вправо
            if c + streak <= size:
                if all(b[r][c+i] == player for i in range(streak)):
                    return player, [(r, c+i) for i in range(streak)]
            # Перевірка вниз
            if r + streak <= size:
                if all(b[r+i][c] == player for i in range(streak)):
                    return player, [(r+i, c) for i in range(streak)]
            # Перевірка по діагоналі вправо-вниз
            if r + streak <= size and c + streak <= size:
                if all(b[r+i][c+i] == player for i in range(streak)):
                    return player, [(r+i, c+i) for i in range(streak)]
            # Перевірка по діагоналі вліво-вниз
            if r + streak <= size and c - streak + 1 >= 0:
                if all(b[r+i][c-i] == player for i in range(streak)):
                    return player, [(r+i, c-i) for i in range(streak)]
    
    # Перевірка на нічию (якщо заповнені всі клітинки і немає переможця)
    if all(b[r][c] is not None for r in range(size) for c in range(size)):
        return 'Draw', []
        
    return None, []

# Функція логіки ходу штучного інтелекту (комп'ютера)
def ai_move():
    global board, current_player, winner, winning_cells
    # Знаходження всіх вільних клітинок на дошці
    empty_cells = [(r, c) for r in range(board_dim) for c in range(board_dim) if board[r][c] is None]
    if not empty_cells or winner:
        return
    
    chosen_cell = None
    
    # 1. ШІ перевіряє, чи може він виграти за один хід
    for (r, c) in empty_cells:
        board[r][c] = 'O'
        w, _ = check_win(board, board_dim, win_streak)
        board[r][c] = None
        if w == 'O':
            chosen_cell = (r, c)
            break
            
    # 2. ШІ перевіряє, чи може гравець виграти за один хід, і блокує його
    if not chosen_cell:
        for (r, c) in empty_cells:
            board[r][c] = 'X'
            w, _ = check_win(board, board_dim, win_streak)
            board[r][c] = None
            if w == 'X':
                chosen_cell = (r, c)
                break
                
    # 3. Інакше обирає випадкову або стратегічну клітинку
    if not chosen_cell:
        if difficulty == 'easy':
            chosen_cell = random.choice(empty_cells)
        elif difficulty == 'medium':
            # Середній рівень: пріоритет центру з певною ймовірністю
            center = board_dim // 2
            if (center, center) in empty_cells and random.random() < 0.6:
                chosen_cell = (center, center)
            else:
                chosen_cell = random.choice(empty_cells)
        else: # складний рівень (hard)
            # Високий рівень: частіше обирає центр або випадкову вільну
            center = board_dim // 2
            if (center, center) in empty_cells and random.random() < 0.7:
                chosen_cell = (center, center)
            else:
                chosen_cell = random.choice(empty_cells)
                
    # Здійснення ходу комп'ютером у вибрану клітинку
    if chosen_cell:
        board[chosen_cell[0]][chosen_cell[1]] = 'O'
        winner, winning_cells = check_win(board, board_dim, win_streak)
        if winner:
            if winner != 'Draw' and win_sound and sound_enabled:
                win_sound.play() # Відтворення звуку перемоги
            game_state = 'GAME_OVER'
        else:
            current_player = 'X' # Передача ходу гравцю

# Головні змінні циклу гри
running = True
paused_from_state = 'PLAYING' # Запам'ятовування стану, з якого була викликана пауза

# Головний ігровий цикл
while running:
    screen.fill(BG_COLOR) # Заповнення екрана фоновим кольором на кожному кадрі
    
    mouse_pos = pygame.mouse.get_pos() # Отримання поточних координат курсора миші
    
    # Обробка подій (натискання клавіш, закриття вікна, кліки мишею)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False # Вихід з ігрового циклу при закритті вікна
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Обробка кліків у Головному меню
            if game_state == 'MENU':
                if play_button.collidepoint(mouse_pos):
                    game_state = 'DIFFICULTY' # Перехід до вибору складності
                elif exit_button.collidepoint(mouse_pos):
                    running = False # Вихід з гри
                    
            # Обробка кліків у меню вибору складності
            elif game_state == 'DIFFICULTY':
                if diff_easy_btn.collidepoint(mouse_pos):
                    difficulty = 'easy'
                    board_dim, win_streak, _ = setup_board(difficulty)
                    board = [[None for _ in range(board_dim)] for _ in range(board_dim)]
                    winner = None
                    winning_cells = []
                    current_player = 'X'
                    game_state = 'PLAYING'
                elif diff_med_btn.collidepoint(mouse_pos):
                    difficulty = 'medium'
                    board_dim, win_streak, _ = setup_board(difficulty)
                    board = [[None for _ in range(board_dim)] for _ in range(board_dim)]
                    winner = None
                    winning_cells = []
                    current_player = 'X'
                    game_state = 'PLAYING'
                elif diff_hard_btn.collidepoint(mouse_pos):
                    difficulty = 'hard'
                    board_dim, win_streak, _ = setup_board(difficulty)
                    board = [[None for _ in range(board_dim)] for _ in range(board_dim)]
                    winner = None
                    winning_cells = []
                    current_player = 'X'
                    game_state = 'PLAYING'
                    
            # Обробка кліків під час гри або закінчення гри (бокова панель керування)
            elif game_state in ['PLAYING', 'GAME_OVER']:
                # Перевірка натискання кнопок керування
                if reset_btn.collidepoint(mouse_pos):
                    board = [[None for _ in range(board_dim)] for _ in range(board_dim)]
                    winner = None
                    winning_cells = []
                    current_player = 'X'
                    game_state = 'PLAYING'
                elif pause_btn.collidepoint(mouse_pos):
                    paused_from_state = game_state
                    game_state = 'PAUSED'
                elif sound_btn.collidepoint(mouse_pos):
                    sound_enabled = not sound_enabled
                    if sound_enabled:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                elif menu_btn.collidepoint(mouse_pos):
                    game_state = 'MENU'
                    
                # Обробка кліків по ігровому полю, якщо зараз хід гравця ('X')
                elif game_state == 'PLAYING' and current_player == 'X':
                    board_size_px = 520
                    start_x, start_y = 50, 40
                    # Перевірка, чи клік припав всередину ігрової дошки
                    if start_x <= mouse_pos[0] <= start_x + board_size_px and start_y <= mouse_pos[1] <= start_y + board_size_px:
                        cell_w = board_size_px / board_dim
                        c = int((mouse_pos[0] - start_x) // cell_w)
                        r = int((mouse_pos[1] - start_y) // cell_w)
                        # Перевірка валідності клітинки та чи вона вільна
                        if 0 <= r < board_dim and 0 <= c < board_dim and board[r][c] is None:
                            board[r][c] = 'X'
                            winner, winning_cells = check_win(board, board_dim, win_streak)
                            if winner:
                                if winner != 'Draw' and win_sound and sound_enabled:
                                    win_sound.play()
                                game_state = 'GAME_OVER'
                            else:
                                current_player = 'O' # Передача ходу комп'ютеру
                                
            # Обробка кліків у стані Паузи
            elif game_state == 'PAUSED':
                if pause_btn.collidepoint(mouse_pos) or menu_btn.collidepoint(mouse_pos):
                    if pause_btn.collidepoint(mouse_pos):
                        game_state = paused_from_state
                    elif menu_btn.collidepoint(mouse_pos):
                        game_state = 'MENU'

    # Штучний інтелект робить хід з невеликою затримкою для природності
    if game_state == 'PLAYING' and current_player == 'O' and not winner:
        pygame.time.delay(300) # Затримка 300 мс
        ai_move()

    # Відображення елементів на екрані залежно від поточного ігрового стану
    if game_state == 'MENU':
        title_surf = big_font.render("Cross Dot", True, WHITE)
        screen.blit(title_surf, (w // 2 - title_surf.get_width() // 2, 120))
        
        # Малювання кнопок меню з заокругленими кутами
        pygame.draw.rect(screen, BLUE, play_button, border_radius=8)
        pygame.draw.rect(screen, RED, exit_button, border_radius=8)
        
        play_txt = font.render("PLAY", True, WHITE)
        exit_txt = font.render("EXIT", True, WHITE)
        screen.blit(play_play := play_txt, (play_button.centerx - play_play.get_width()//2, play_button.centery - play_play.get_height()//2))
        screen.blit(exit_t := exit_txt, (exit_button.centerx - exit_t.get_width()//2, exit_button.centery - exit_t.get_height()//2))

    elif game_state == 'DIFFICULTY':
        title_surf = big_font.render("Select Difficulty", True, WHITE)
        screen.blit(title_surf, (w // 2 - title_surf.get_width() // 2, 80))
        
        # Малювання кнопок вибору складності
        pygame.draw.rect(screen, GREEN, diff_easy_btn, border_radius=8)
        pygame.draw.rect(screen, BLUE, diff_med_btn, border_radius=8)
        pygame.draw.rect(screen, RED, diff_hard_btn, border_radius=8)
        
        screen.blit(font.render("Easy (3x3 - Win: 3)", True, WHITE), (diff_easy_btn.centerx - 100, diff_easy_btn.centery - 12))
        screen.blit(font.render("Medium (8x8 - Win: 4)", True, WHITE), (diff_med_btn.centerx - 110, diff_med_btn.centery - 12))
        screen.blit(font.render("Hard (12x12 - Win: 6)", True, WHITE), (diff_hard_btn.centerx - 110, diff_hard_btn.centery - 12))

    elif game_state in ['PLAYING', 'PAUSED', 'GAME_OVER']:
        # Рендеринг ігрової сітки (дошки)
        board_size_px = 520
        start_x, start_y = 50, 40
        cell_w = board_size_px / board_dim
        
        for i in range(board_dim + 1):
            # Вертикальні лінії сітки
            pygame.draw.line(screen, GRAY, (start_x + i * cell_w, start_y), (start_x + i * cell_w, start_y + board_size_px), 2)
            # Горизонтальні лінії сітки
            pygame.draw.line(screen, GRAY, (start_x, start_y + i * cell_w), (start_x + board_size_px, start_y + i * cell_w), 2)
            
        # Рендеринг фігур Хрестиків (X) та Нуликів/Точок (O) у клітинках
        for r in range(board_dim):
            for c in range(board_dim):
                cell_val = board[r][c]
                cx = start_x + c * cell_w + cell_w / 2
                cy = start_y + r * cell_w + cell_w / 2
                if cell_val == 'X':
                    # Малювання хрестика
                    offset = cell_w * 0.3
                    pygame.draw.line(screen, BLUE, (cx - offset, cy - offset), (cx + offset, cy + offset), max(2, int(4 - board_dim/4)))
                    pygame.draw.line(screen, BLUE, (cx - offset, cy + offset), (cx + offset, cy - offset), max(2, int(4 - board_dim/4)))
                elif cell_val == 'O':
                    # Малювання кола (точки)
                    radius = int(cell_w * 0.3)
                    pygame.draw.circle(screen, RED, (int(cx), int(cy)), radius, max(2, int(4 - board_dim/4)))
                    
        # Підсвічування виграшних клітинок зеленим кольором
        if winning_cells:
            for (r, c) in winning_cells:
                rx = start_x + c * cell_w
                ry = start_y + r * cell_w
                pygame.draw.rect(screen, GREEN, (rx, ry, cell_w, cell_w), 4)

        # Малювання бічної панелі з кнопками керування
        pygame.draw.rect(screen, BLUE, reset_btn, border_radius=6)
        pygame.draw.rect(screen, DARK_GRAY, pause_btn, border_radius=6)
        pygame.draw.rect(screen, BLUE, sound_btn, border_radius=6)
        pygame.draw.rect(screen, RED, menu_btn, border_radius=6)
        
        # Текст на кнопках бокової панелі
        screen.blit(font.render("Reset", True, WHITE), (reset_btn.centerx - 25, reset_btn.centery - 12))
        screen.blit(font.render("Pause" if game_state != 'PAUSED' else "Resume", True, WHITE), (pause_btn.centerx - 30, pause_btn.centery - 12))
        screen.blit(font.render("Sound: " + ("ON" if sound_enabled else "OFF"), True, WHITE), (sound_btn.centerx - 45, sound_btn.centery - 12))
        screen.blit(font.render("Menu", True, WHITE), (menu_btn.centerx - 25, menu_btn.centery - 12))
        
        # Відображення статусного рядка внизу екрана
        status_y = 570
        if game_state == 'GAME_OVER':
            if winner == 'Draw':
                txt = font.render("Нічия! Гра завершена.", True, WHITE)
            else:
                txt = font.render(f"Переможець: {winner}!", True, GREEN)
            screen.blit(txt, (50, status_y))
        elif game_state == 'PAUSED':
            pause_overlay = font.render("ПАУЗА", True, WHITE)
            screen.blit(pause_overlay, (250, status_y))
        else:
            turn_txt = font.render(f"Хід гравця: {current_player} ({'Ви' if current_player=='X' else 'Компʼютер'})", True, WHITE)
            screen.blit(turn_txt, (50, status_y))

    pygame.display.flip() # Оновлення екрана для виведення намальованого кадру
    clock.tick(60) # Обмежувач на 60 кадрів на секунду

pygame.quit() # Коректне завершення роботи бібліотеки pygame при виході з програми