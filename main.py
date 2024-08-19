import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import random
import math


# Константы
ROWS = 8
COLS = 3
CELL_SIZE = 150
ANOMALY_SIZE = CELL_SIZE // 4
WINNING_POINTS = 20  # Константа для победы
HAND_SIZE = 5
DECK_SIZE = 20
MANA = 2

# Глобальные переменные
players = []
current_player = 0
current_mana = 0
selected_card_index = None
PLAYERS_HP_COUNT = [0, 0]

row_old = 0
col_old = 0

def generate_deck():
    deck = []
    directions = ['up', 'down', 'left', 'right']
    action_types = ['attack', 'heal']

    for i in range(DECK_SIZE):
        attack = random.randint(1, 10)
        hp = random.randint(1, 10)
        price = (attack + math.ceil(0.5 * hp)) // 2

        direction = random.choice(directions)
        range_ = random.randint(1, 3)
        action_type = random.choice(action_types)

        deck.append({
            "price": price,
            "attack": attack,
            "hp": hp,
            "direction": direction,
            "range": range_,
            "action_type": action_type
        })
    random.shuffle(deck)
    return deck

def draw_initial_hand(deck):
    hand = []
    for _ in range(HAND_SIZE):
        hand.append(deck.pop())
    return hand

def draw_card(player):
    if player["deck"]:
        player["hand"].append(player["deck"].pop())

def init_game():
    global players, current_mana
    players = [
        {
            "name": "Player 1",
            "deck": generate_deck(),
            "hand": [],
            "field": [[None for _ in range(COLS)] for _ in range(2)],
            "mana": MANA
        },
        {
            "name": "Player 2",
            "deck": generate_deck(),
            "hand": [],
            "field": [[None for _ in range(COLS)] for _ in range(2)],
            "mana": MANA
        }
    ]
    for player in players:
        player["hand"] = draw_initial_hand(player["deck"])
    current_mana = MANA

def draw_field(canvas):
    for row in range(ROWS // 2 - 2, ROWS // 2):
        for col in range(COLS):
            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE

            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            canvas.create_rectangle(x1, y1, x2, y2, outline='black', fill='lightgreen', tags=['field', 'enemy'])

    for row in range(ROWS // 2, ROWS - 2):
        for col in range(COLS):
            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE

            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            canvas.create_rectangle(x1, y1, x2, y2, outline='black', fill='green', tags=['field', 'hero'])

def draw_hands(canvas):
    canvas.delete("hand")
    for idx in range(3):  # Отображаем по 3 карты в ряду
        card = players[0]["hand"][idx] if idx < len(players[0]["hand"]) else None
        x = idx * CELL_SIZE
        y = (ROWS - 2) * CELL_SIZE
        draw_card_in_hand(canvas, x, y, card)

    for idx in range(3, HAND_SIZE):  # Отображаем второй ряд карт
        card = players[0]["hand"][idx] if idx < len(players[0]["hand"]) else None
        x = (idx - 3) * CELL_SIZE
        y = (ROWS - 1) * CELL_SIZE
        draw_card_in_hand(canvas, x, y, card)

    for idx in range(3):  # Отображаем по 3 карты в верхнем ряду
        card = players[1]["hand"][idx] if idx < len(players[1]["hand"]) else None
        x = idx * CELL_SIZE
        y = 0
        draw_card_in_hand(canvas, x, y, card)

    for idx in range(3, HAND_SIZE):  # Отображаем второй ряд верхних карт
        card = players[1]["hand"][idx] if idx < len(players[1]["hand"]) else None
        x = (idx - 3) * CELL_SIZE
        y = CELL_SIZE
        draw_card_in_hand(canvas, x, y, card)

def draw_card_in_hand(canvas, x, y, card):
    canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill='white', tags="hand")
    if card:
        canvas.create_text(
            x + CELL_SIZE // 2, y + CELL_SIZE // 2,
            text=f"Цена: {card['price']}\nАтака: {card['attack']}\nЗдоровье: {card['hp']}\nДействие: {card['action_type']}\nНаправление: {card['direction']}\nДальность: {card['range']}",
            tags="hand"
        )

def calculate_total_health(player):
    total_health = 0

    for row in player["field"]:
        for card in row:
            if card is not None:  # Проверяем, есть ли карта в этой ячейке
                total_health += card["hp"]
    return total_health

def draw_status(canvas):
    global current_mana
    canvas.images = []

    y_offset = ROWS * CELL_SIZE
    x_offset = 0
    status_width = COLS * CELL_SIZE

    canvas.create_rectangle(x_offset, y_offset, x_offset + status_width, y_offset + CELL_SIZE // 4, fill='blue')
    canvas.create_text(x_offset + status_width // 2, y_offset + CELL_SIZE // 8, text=f"Mana: {current_mana} | ход {current_player} игрока", fill='white')

    y_center = 3 * CELL_SIZE
    x_center = COLS * CELL_SIZE // 2

    PLAYERS_HP_COUNT[0] = calculate_total_health(players[0])
    PLAYERS_HP_COUNT[1] = calculate_total_health(players[1])

    draw_large_text_with_transparency(canvas, str(PLAYERS_HP_COUNT[0]), x_center, y_center + 2 * CELL_SIZE)
    draw_large_text_with_transparency(canvas, str(PLAYERS_HP_COUNT[1]), x_center, y_center)

    canvas.create_text(CELL_SIZE * 2.5, CELL_SIZE * 1.5, text="ЗАКОНЧИТЬ\nХОД", anchor='center')
    canvas.create_text(CELL_SIZE * 2.5, CELL_SIZE * 7.5, text="ЗАКОНЧИТЬ\nХОД", anchor='center')

def on_click(event, canvas):
    global selected_card_index, turn_stage, current_player, current_mana, col_old, row_old

    # Вычисляем строку и столбец на игровом поле
    row = event.y // CELL_SIZE
    col = event.x // CELL_SIZE

    if (current_player == 0 and row == 7 and col == 2) or (current_player == 1 and row == 1 and col == 2):
        next_turn(canvas)

    print(f'Координаты клика: row {row}, col {col}')

    if (1 - current_player)*6 <= row <= (1 - current_player)*6 + 1 and 0 <= col <= COLS:
        card_index = col + (row - (1 - current_player)*6) * COLS
        print(f'выбрана {card_index} карта {current_player}-го игрока')
        if 0 <= card_index < len(players[current_player]["hand"]):
            selected_card_index = card_index
            row_old = row
            col_old = col
            print(f'Выбрана карта героя с индексом: {selected_card_index}')
            # Проверяем клик по полю героя

    elif (1 - current_player)*2 + 2 <= row < (1 - current_player)*2 + 4 and 0 <= col <= COLS:
        if selected_card_index is not None and players[current_player]['hand'][selected_card_index]['price'] <= current_mana:
            current_mana -= players[current_player]['hand'][selected_card_index]['price']
            canvas.create_rectangle(col_old*CELL_SIZE, row_old*CELL_SIZE, (col_old+1)*CELL_SIZE, (row_old+1)*CELL_SIZE, fill='yellow')
            place_card(canvas, row, col, selected_card_index)
            #draw_status(canvas)
            selected_card_index = None

def place_card(canvas, row, col, card_index):
    global current_player
    current_field = players[current_player]["field"]

    local_row = row - (ROWS - 4) if current_player == 0 else row - 2

    # Проверяем, что мы в пределах поля данного игрока
    if 0 <= local_row < 2 and 0 <= col < COLS:

        if current_field[local_row][col] is None:
            card = players[current_player]["hand"].pop(card_index)
            current_field[local_row][col] = card

            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE

            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            canvas.create_rectangle(x1, y1, x2, y2, fill='gray')
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                               text=f"Стоимость {card['price']}\nАтака {card['attack']}\nЗдоровье {card['hp']}\nДействие: {card['action_type']}\nНаправление: {card['direction']}\nДальность: {card['range']}")

            draw_status(canvas)
            check_for_win(canvas)  # Проверяем на победу


def draw_large_text_with_transparency(canvas, text, x_center, y_center):
    """Отображает прозрачный текст с использованием изображения"""
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=180)

    draw.text((0, 0), text, font=font, fill=(255, 255, 255, 128))

    img_tk = ImageTk.PhotoImage(img)
    image_id = canvas.create_image(x_center, y_center, image=img_tk, anchor='center')
    canvas.images.append(img_tk)  # Сохранение изображения

    canvas.tag_raise(image_id)


def check_for_win(canvas):
    """Проверяет, есть ли победитель, и отображает сообщение"""
    for i in range(2):
        if PLAYERS_HP_COUNT[i] >= WINNING_POINTS:
            canvas.create_text(CELL_SIZE * COLS // 2, CELL_SIZE * ROWS // 2,
                               text=f"Выиграл игрок {i}!",
                               font=("Helvetica", 32),
                               fill="red")
            return True  # Завершаем игру


def next_turn(canvas):
    global current_player, current_mana

    apply_card_effects(canvas)

    if current_player == 1:
        players[current_player]["mana"] += 1
        players[current_player - 1]["mana"] += 1

    current_mana = players[current_player]['mana']

    current_player = 1 - current_player
    draw_card(players[current_player])   # добор карты
    draw_hands(canvas)

    print(f'переход хода. ходит {current_player} игрок')
    draw_status(canvas)


def apply_card_effects(canvas):
    global current_player
    opponent_player = 1 - current_player

    # Обрабатываем карты текущего игрока
    for row in range(2):
        for col in range(COLS):
            current_card = players[current_player]["field"][row][col]
            if current_card:
                if current_card["action_type"] == "attack":
                    apply_attack(canvas, row, col, current_card, players[opponent_player]["field"])
                elif current_card["action_type"] == "heal":
                    apply_heal(canvas, row, col, current_card, players[current_player]["field"])

                # Обновляем отображение карты с учетом новых параметров
                update_card_display(canvas, row + (ROWS - 4) * current_player - 2, col, current_card)

    draw_status(canvas)  # Обновляем статус после выполнения всех эффектов
    check_for_win(canvas)


def update_card_display(canvas, row, col, card):
    x1 = col * CELL_SIZE
    y1 = row * CELL_SIZE
    x2 = x1 + CELL_SIZE
    y2 = y1 + CELL_SIZE

    canvas.create_rectangle(x1, y1, x2, y2, fill='gray')
    canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                       text=f"Стоимость {card['price']}\nАтака {card['attack']}\nЗдоровье {card['hp']}\nДействие: {card['action_type']}\nНаправление: {card['direction']}\nДальность: {card['range']}")


def apply_attack(canvas, row, col, card, target_field):
    directions = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }
    dr, dc = directions[card["direction"]]

    for r in range(1, card["range"] + 1):
        target_row = row + r * dr
        target_col = col + r * dc

        if 0 <= target_row < 2 and 0 <= target_col < COLS:
            target_card = target_field[target_row][target_col]
            if target_card:
                target_card["hp"] -= card["attack"]

                if target_card["hp"] <= 0:
                    target_field[target_row][target_col] = None
                    fill = 'green' if row >= 4 else 'lightgreen'
                    canvas.create_rectangle(target_col * CELL_SIZE,
                                            (target_row + (ROWS - 4) * (1 - current_player)) * CELL_SIZE,
                                            (target_col + 1) * CELL_SIZE,
                                            (target_row + (ROWS - 4) * (1 - current_player) + 1) * CELL_SIZE,
                                            fill=fill)#'lightgreen')
                else:
                    update_card_display(canvas, target_row + (ROWS - 4) * (1 - current_player), target_col, target_card)


def apply_heal(canvas, row, col, card, target_field):
    directions = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }
    dr, dc = directions[card["direction"]]

    for r in range(1, card["range"] + 1):
        target_row = row + r * dr
        target_col = col + r * dc

        if 0 <= target_row < 2 and 0 <= target_col < COLS:
            target_card = target_field[target_row][target_col]
            if target_card:

                target_card["hp"] += card["attack"]
                update_card_display(canvas, target_row + (ROWS - 4) * (1 - current_player), target_col, target_card)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Card Game")

    init_game()

    canvas = tk.Canvas(root, width=COLS * CELL_SIZE,
                                height=ROWS * CELL_SIZE + ANOMALY_SIZE,
                                bg='yellow')
    canvas.pack()

    draw_field(canvas)
    draw_hands(canvas)
    draw_status(canvas)

    canvas.bind("<Button-1>", lambda event: on_click(event, canvas))

    root.mainloop()
