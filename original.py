#!/usr/bin/env python3
from math import inf as infinity
from random import choice
import platform
import time
from os import system
from copy import deepcopy
"""
An implementation of Minimax AI Algorithm in Tic Tac Toe,
using Python.
This software is available under GPL license.
Author: Clederson Cruz, Tuan Au Duong
Year: 2023
License: GNU GENERAL PUBLIC LICENSE (GPL)
"""

HUMAN = -1
COMP = +1
BOARD_SIZE = 10
# Large board size -> need to limit the depth
DEPTH_LIMIT = 3
WIN_STREAK = 5
TIME_LIMIT = 2.0
board = [[0 for j in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]
moves = {}
mcurrentIndex = 1
for mx in range(BOARD_SIZE):
    for my in range(BOARD_SIZE):
        moves[mcurrentIndex] = [mx, my]
        mcurrentIndex += 1
start_time = [time.time()]


def generate_checkmate(player):
    checkmates = []
    for i in range(1, WIN_STREAK+1):
        checkmates.append([player]*(WIN_STREAK-i)+[0]+[player]*(i-1))
    return checkmates


def generate_half_checkmate(player):
    half_checkmates = []
    for i in range(1, WIN_STREAK):
        template = [0]+[player]*(WIN_STREAK-1)+[0]
        template[i] = 0
        half_checkmates.append(template)
    return half_checkmates


human_checkmate_list = generate_checkmate(HUMAN)
comp_checkmate_list = generate_checkmate(COMP)
human_half_checkmate_list = generate_half_checkmate(HUMAN)
comp_half_checkmate_list = generate_half_checkmate(COMP)


def get_win_paths():
    win_paths = []
    for i in range(BOARD_SIZE):
        # x = b
        xb = []
        # y = b
        yb = []
        for k in range(BOARD_SIZE):
            xb.append([i, k])
            yb.append([k, i])
        win_paths.append(xb)
        win_paths.append(yb)
    b = BOARD_SIZE-WIN_STREAK+1
    for k in range(-b+1, b):
        # y = x + k
        yxk = []
        for x in range(BOARD_SIZE):
            y = x+k
            if (y >= 0 and y < BOARD_SIZE):
                yxk.append([x, y])
        if (len(yxk) > 0):
            win_paths.append(yxk)

        # y = BOARD_SIZE - 1 - x + k
        y_sxk = []
        for x in range(BOARD_SIZE):
            y = BOARD_SIZE - 1 - x + k
            if (y >= 0 and y < BOARD_SIZE):
                y_sxk.append([x, y])
        if (len(y_sxk) > 0):
            win_paths.append(y_sxk)

    return win_paths


def get_win_cases_in_state(state):
    win_cases_in_state = []
    win_paths = get_win_paths()
    for path in win_paths:
        win_cases_in_state.append(
            list(map(lambda pos: state[pos[0]][pos[1]], path)))
    return win_cases_in_state


def heuristic(state, previous_move):
    c_win_point = 0
    h_win_point = 0
    # 1. neu co ben win => tra ve ket qua lien
    if wins(state, COMP):
        c_win_point += 1000
        return c_win_point - h_win_point
    if wins(state, HUMAN):
        h_win_point += 1000
        return c_win_point - h_win_point
    # 2. tim cac checkmate
    # previous state: curent state remove previous move
    previous_state = deepcopy(state)
    previous_state[previous_move[0]][previous_move[1]] = 0
    # tim cac win case truoc va sau
    current_win_cases = get_win_cases_in_state(state)
    previous_win_cases = get_win_cases_in_state(previous_state)
    # cac mang checkmate, 0: COMP, 1: COMP - HALF, 2: HUMAN, 3: HUMAN - HALF
    current_checkmates = find_checkmates(current_win_cases)
    previous_checkmates = find_checkmates(previous_win_cases)
    # CHECKMATE
    # neu nuoc nay chan checkmate => uu tien
    human_checkmate_difference = len(
        current_checkmates["human"]) - len(previous_checkmates["human"])
    if human_checkmate_difference < 0:
        c_win_point += 300*(-human_checkmate_difference)
    else:
        h_win_point += 300*human_checkmate_difference
    comp_checkmate_difference = len(
        current_checkmates["comp"]) - len(previous_checkmates["comp"])
    # neu nuoc nay chan checkmate cua con comp
    if comp_checkmate_difference < 0:
        h_win_point += 250*(-comp_checkmate_difference)
    # neu nuoc nay mo them checkmate cho comp
    else:
        c_win_point += 250*comp_checkmate_difference
    # HALF CHECKMATE
    # neu nuoc nay chan half checkmate => uu tien
    human_half_checkmate_difference = len(
        current_checkmates["human_half"]) - len(previous_checkmates["human_half"])
    if human_half_checkmate_difference < 0:
        c_win_point += 200*(-human_half_checkmate_difference)
    else:
        h_win_point += 200*human_checkmate_difference
    comp_half_checkmate_difference = len(
        current_checkmates["comp_half"]) - len(previous_checkmates["comp_half"])
    # xet half checkmate
    if comp_half_checkmate_difference < 0:
        h_win_point += 150*(-comp_half_checkmate_difference)
    else:
        c_win_point += 150*comp_half_checkmate_difference
    # con lai, dem so nuoc lien ke trong win path
    for path in current_win_cases:
        count_c = count_consecutive_duplicates(COMP, path)
        c_next_opponent = count_c[1]
        c_prev_opponent = count_c[1]-count_c[0]-1
        count_h = count_consecutive_duplicates(HUMAN, path)
        h_next_opponent = count_h[1]
        h_prev_opponent = count_h[1]-count_h[0]-1

        if (HUMAN not in path):
            c_win_point += count_c[0]*2
            # neu comp chua co thi uu tien phan o giua ban va gan human
        else:
            # neu doi thu nam sat ben => cong them diem doi thu de chan truoc
            if (c_next_opponent < len(path) and path[c_next_opponent] == HUMAN) or (c_prev_opponent > -1 and path[c_prev_opponent] == HUMAN):
                c_win_point += count_c[0]*1 + count_h[0]*1
            else:
                c_win_point += count_c[0]*2

        if (COMP not in path):
            h_win_point += count_h[0]*2
            # neu comp chua co thi uu tien phan o giua ban va gan human
        else:
            if (h_next_opponent < len(path) and path[h_next_opponent] == COMP) or (h_prev_opponent > -1 and path[h_prev_opponent] == COMP):
                h_win_point += count_h[0]*1 + count_c[0]*1
            else:
                h_win_point += count_h[0]*2

    # none edge priority - uu tien di o trong hon la o canh
    if previous_move[0] != 0 and previous_move[0] != 1 and previous_move[0] != BOARD_SIZE - 1 and previous_move[0] != BOARD_SIZE - 2:
        if previous_move[1] != 0 and previous_move[1] != 1 and previous_move[1] != BOARD_SIZE - 1 and previous_move[1] != BOARD_SIZE - 2:
            c_win_point += 2

    return c_win_point - h_win_point

    # return score


def is_slice_in_list(s, l):
    len_s = len(s)
    return any(s == l[i:len_s+i] for i in range(len(l) - len_s+1))

# Dem so luot lap lai lien tiep
# Tra ve so luong va index cuoi cung
def count_consecutive_duplicates(s, l):
    count = 0
    maxCount = 0
    nextOpponent = 0
    for i, n in enumerate(l):
        if (n == s):
            count += 1
        else:
            if (count > maxCount):
                maxCount = count
                nextOpponent = i
            count = 0
    if (count > maxCount):
        maxCount = count
        nextOpponent = i
    return [maxCount, nextOpponent]


def wins(state, player):
    win_cases_in_state = get_win_cases_in_state(state)
    for win_case in win_cases_in_state:
        if is_slice_in_list([player]*WIN_STREAK, win_case):
            return True
    return False


def game_over(state):
    """
    This function test if the human or computer wins
    :param state: the state of the current board
    :return: True if the human or computer wins
    """
    return wins(state, HUMAN) or wins(state, COMP)


def empty_cells(state):
    """
    Each empty cell will be added into cells' list
    :param state: the state of the current board
    :return: a list of empty cells
    """
    cells = []

    for x, row in enumerate(state):
        for y, cell in enumerate(row):
            if cell == 0:
                cells.append([x, y])

    return cells


def valid_move(x, y):
    """
    A move is valid if the chosen cell is empty
    :param x: X coordinate
    :param y: Y coordinate
    :return: True if the board[x][y] is empty
    """
    if [x, y] in empty_cells(board):
        return True
    else:
        return False


def set_move(x, y, player):
    """
    Set the move on board, if the coordinates are valid
    :param x: X coordinate
    :param y: Y coordinate
    :param player: the current player
    """
    if valid_move(x, y):
        board[x][y] = player
        return True
    else:
        return False


def minimax(state, depth, alpha, beta, player, previous_move):
    """
    AI function that choice the best move
    :param state: current state of the board
    :param depth: node index in the tree (0 <= depth <= 9),
    but never nine in this case (see iaturn() function)
    :param player: an human or a computer
    :return: a list with [the best row, best col, best score]
    """
    if player == COMP:
        best = [-1, -1, -infinity]
    else:
        best = [-1, -1, +infinity]
    current_depth = len(empty_cells(board))
    if depth == 0 or game_over(state) or depth < current_depth - DEPTH_LIMIT or (time.time() - start_time[0] > TIME_LIMIT):
        score = heuristic(state, previous_move)
        return [-1, -1, score]

    for cell in empty_cells(state):
        # toa do cua cai move toi
        x, y = cell[0], cell[1]
        # dien vao o trong de tao ra state
        state[x][y] = player
        # ghi nho nuoc di vua roi
        # danh gia trang thai khi di
        score = minimax(state, depth - 1, alpha, beta, -player, cell)
        # reset lai trang thai
        state[x][y] = 0
        score[0], score[1] = x, y

        if player == COMP:
            if score[2] > best[2]:
                best = score  # max value
            alpha = max(alpha, score[2])
            if beta <= alpha:
                break
        else:
            if score[2] < best[2]:
                best = score  # min value
            beta = min(beta, score[2])
            if beta <= alpha:
                break

    return best


def clean():
    """
    Clears the console
    """
    os_name = platform.system().lower()
    if 'windows' in os_name:
        system('cls')
    else:
        system('clear')


def render(state, c_choice, h_choice):
    """
    Print the board on console
    :param state: current state of the board
    """

    chars = {
        -1: h_choice,
        +1: c_choice,
        0: ' '
    }
    str_line = '------'+('------'*BOARD_SIZE)

    print('\n' + str_line)
    print('     ', end='')
    for col_n in range(1, BOARD_SIZE+1):
        if (col_n > 9):
            print(f'|  {col_n} ', end='')
        else:
            print(f'|  {col_n}  ', end='')
    print('\n' + str_line)
    for row_n, row in enumerate(state):
        letter = chr(ord('@')+row_n+1)
        print(f' {letter}   ', end='')
        for cell in row:
            symbol = chars[cell]
            print(f'|  {symbol}  ', end='')
        print('\n' + str_line)


def find_checkmates(win_cases_in_state):
    found_comp_checkmate = []
    found_comp_half_checkmate = []
    found_human_checkmate = []
    found_human_half_checkmate = []
    for path in win_cases_in_state:
        for checkmate in human_checkmate_list:
            if (is_slice_in_list(checkmate, path)):
                found_human_checkmate.append(checkmate)
        for half_checkmate in human_half_checkmate_list:
            if (is_slice_in_list(half_checkmate, path)):
                found_human_half_checkmate.append(half_checkmate)
        for checkmate in comp_checkmate_list:
            if (is_slice_in_list(checkmate, path)):
                found_comp_checkmate.append(checkmate)
        for half_checkmate in comp_half_checkmate_list:
            if (is_slice_in_list(half_checkmate, path)):
                found_comp_half_checkmate.append(half_checkmate)
    return {"comp": found_comp_checkmate, "comp_half": found_comp_half_checkmate, "human": found_human_checkmate, "human_half": found_human_half_checkmate}


def ai_turn(c_choice, h_choice):
    """
    It calls the minimax function if the depth < 9,
    else it choices a random coordinate.
    :param c_choice: computer's choice X or O
    :param h_choice: human's choice X or O
    :return:
    """
    depth = len(empty_cells(board))
    start_time[0] = time.time()
    if depth == 0 or game_over(board):
        return

    clean()
    print(f'Computer turn [{c_choice}]')
    render(board, c_choice, h_choice)
    print('AI is loading...')

    # neu di dau => chon ngau nhien cac nuoc di giua ban
    if depth == BOARD_SIZE * BOARD_SIZE:
        random_choices = [BOARD_SIZE//2-1, BOARD_SIZE//2, BOARD_SIZE//2+1]
        x = choice(random_choices)
        y = choice(random_choices)
    else:
        move = minimax(deepcopy(board), depth, -infinity, infinity, COMP, [])
        x, y = move[0], move[1]

    set_move(x, y, COMP)
    time.sleep(1)


def human_turn(c_choice, h_choice):
    """
    The Human plays choosing a valid move.
    :param c_choice: computer's choice X or O
    :param h_choice: human's choice X or O
    :return:
    """
    depth = len(empty_cells(board))
    if depth == 0 or game_over(board):
        return

    # Dictionary of valid moves
    move = -1
    clean()
    print(f'Human turn [{h_choice}]')
    render(board, c_choice, h_choice)

    while move < 1 or move > BOARD_SIZE*BOARD_SIZE:
        try:
            moveStr = input(
                'Enter position (A1, A2, ..., A'+str(BOARD_SIZE)+'): ')
            move = (ord(moveStr[0])-ord('A'))*BOARD_SIZE + int(moveStr[1:])
            print('Move', move)
            coord = moves[move]
            can_move = set_move(coord[0], coord[1], HUMAN)

            if not can_move:
                print('Bad move')
                move = -1
        except (EOFError, KeyboardInterrupt):
            print('Bye')
            exit()
        except (KeyError, ValueError):
            print('Bad choice')


def main():
    """
    Main function that calls all functions
    """
    clean()
    h_choice = ''  # X or O
    c_choice = ''  # X or O
    first = ''  # if human is the first

    # Human chooses X or O to play
    while h_choice != 'O' and h_choice != 'X':
        try:
            print('')
            h_choice = input('Choose X or O\nChosen: ').upper()
        except (EOFError, KeyboardInterrupt):
            print('Bye')
            exit()
        except (KeyError, ValueError):
            print('Bad choice')

    # Setting computer's choice
    if h_choice == 'X':
        c_choice = 'O'
    else:
        c_choice = 'X'

    clean()
    while first != 'Y' and first != 'N':
        try:
            first = input('First to start?[y/n]: ').upper()
        except (EOFError, KeyboardInterrupt):
            print('Bye')
            exit()
        except (KeyError, ValueError):
            print('Bad choice')
    print('Win streak is', WIN_STREAK)
    # Main loop of this game
    while len(empty_cells(board)) > 0 and not game_over(board):
        if first == 'N':
            ai_turn(c_choice, h_choice)
            first = ''

        human_turn(c_choice, h_choice)
        ai_turn(c_choice, h_choice)

    # Game over message
    if wins(board, HUMAN):
        clean()
        print(f'Human turn [{h_choice}]')
        render(board, c_choice, h_choice)
        print('YOU WIN!')
    elif wins(board, COMP):
        clean()
        print(f'Computer turn [{c_choice}]')
        render(board, c_choice, h_choice)
        print('YOU LOSE!')
    else:
        clean()
        render(board, c_choice, h_choice)
        print('DRAW!')

    exit()


if __name__ == '__main__':
    main()
