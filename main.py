# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing

DEBUG = False

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "alfredo-0815",  # TODO: Your Battlesnake Username
        "color": "#13932f",  # TODO: Choose color
        "head": "all-seeing",  # TODO: Choose head
        "tail": "mouse",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    # return return_move('left', game_state['turn'])
    w = game_state['board']['width']
    h = game_state['board']['height']
    head = game_state['you']['head']
    turn = game_state['turn']
    # todo: causes errors, but should be safer if it works
    aggressive = True

    food = find_closest_food(head, game_state['board']['food'])
    exclude = get_danger_positions(game_state, aggressive)

    q = bs(food, head, w, h, exclude)

    next_move = decide(head, q, w, h, exclude)

    if DEBUG:
        print_state(
            game_state['you']['body'],
            game_state['board']['food'],
            q, w, h
        )
    
    return return_move(next_move, turn)


# -------------------------------------------------------------------------------
# elementary functions


def calculate_distance(p1, p2):
    return abs(p1['x'] - p2['x']) + abs(p1['y'] - p2['y'])


def out_of_bounds(pos, width, height):
    if pos['x'] < 0 or pos['x'] >= width or pos['y'] < 0 or pos['y'] >= height:
        return True
    return False


def moore_nb(pos, width, height):
    nbs = [{
        'x': pos['x'] - 1,
        'y': pos['y']
    }, {
        'x': pos['x'] - 1,
        'y': pos['y'] - 1
    }, {
        'x': pos['x'],
        'y': pos['y'] - 1
    }, {
        'x': pos['x'] + 1,
        'y': pos['y'] - 1
    }, {
        'x': pos['x'] + 1,
        'y': pos['y']
    }, {
        'x': pos['x'] + 1,
        'y': pos['y'] + 1
    }, {
        'x': pos['x'],
        'y': pos['y'] + 1
    }, {
        'x': pos['x'] - 1,
        'y': pos['y'] + 1
    }]
    valid_nbs = []
    for nb in nbs:
        if not out_of_bounds(nb, width, height):
            valid_nbs.append(nb)
    return valid_nbs


def von_neumann_nb(pos, width, height):
    nbs = [
        {
            'x': pos['x'] - 1,
            'y': pos['y']
        },
        {
            'x': pos['x'],
            'y': pos['y'] - 1
        },
        {
            'x': pos['x'] + 1,
            'y': pos['y']
        },
        {
            'x': pos['x'],
            'y': pos['y'] + 1
        },
    ]
    valid_nbs = []
    for nb in nbs:
        if not out_of_bounds(nb, width, height):
            valid_nbs.append(nb)
    return valid_nbs


def return_move(move, turn):
    print(f"MOVE {turn}: {move}")
    return {"move": move}


# -------------------------------------------------------------------------------
# helper functions


def pos_to_tuple(pos):
    return (pos['x'], pos['y'])


def pos_to_dict(pos):
    return {'x': pos[0], 'y': pos[1]}


# backwards-chaining
def find_closest_food(head, foods):
    min_dist = None
    min_i = None
    for i, food in enumerate(foods):
        dist = calculate_distance(head, food)
        if not min_dist or min_dist > dist:
            min_dist = dist
            min_i = i

    return foods[min_i]


def get_danger_positions(game_state: typing.Dict, agressive=False):
    positions = game_state['board']['hazards']
    for snake in game_state['board']['snakes']:
        positions = positions + snake['body']
        if not agressive:
            positions = positions + get_possible_moves(
                snake['body'], game_state['board']['width'],
                game_state['board']['height'])

    return positions


def get_possible_moves(body, width, height):
    moves = von_neumann_nb(body[0], width, height)
    if body[1] in moves:
        moves.remove(body[1])
    return moves


def get_possible_moves2(head, exclude, width, height):
    moves = von_neumann_nb(head, width, height)
    for cell in exclude:
        if cell in moves:
            moves.remove(cell)
    return moves


def get_direction(start, fin):
    if type(start) != tuple:
        start = pos_to_tuple(start)
    if type(fin) != tuple:
        fin = pos_to_tuple(fin)

    if start[0] - fin[0] == -1:
        return 'right'
    if start[0] - fin[0] == 1:
        return 'left'
    if start[1] - fin[1] == -1:
        return 'up'
    if start[1] - fin[1] == 1:
        return 'down'

    return None


def decide(head, q, width, height, exclude):
    best_cell = None
    best_value = None
    for cell in map(pos_to_tuple, von_neumann_nb(head, width, height)):
        if cell in q and (not best_cell or q[cell] < best_value):
            best_value = q[cell]
            best_cell = cell

    if best_cell:
        print(f'{best_cell=}: {best_value} ({q[best_cell]})')
        move = get_direction(head, best_cell)
        if move:
            return move
        print('Warning: best move out of reach')
    else:
        print('Warning: no move selected')

    # search algorythm could not reach head
    naive_moves = get_possible_moves2(head, exclude, width, height)
    if naive_moves:
        cell = random.choice(naive_moves)
        naive_move = get_direction(head, cell)
        if naive_move:
            return naive_move
        print('Warning: naive move out of reach')
    else:
        print('Warning: naive move not available')
    return 'down'

def print_state(body, food, q, w, h):
    moves = von_neumann_nb(body[0], w, h)
    for line in range(h):
        y = h - line - 1
        s = '|'
        for x in range(w):
            cell = {'x': x, 'y': y}
            cell_t = pos_to_tuple(cell)
            if cell == body[0]:
                t = 'H'
            elif cell in body:
                t = 'B'
            elif cell in moves:
                t = 'x'
            else:
                t = '_'

            if cell_t in q:
                n = str(q[cell_t])
                if len(n) < 2:
                    n = n + '_'
            else:
                n = '__'

            s = s + f'{t}{n}|'
        print(s)

# -------------------------------------------------------------------------------
# search algorythms


def bs(start, goal, width, height, exclude):
    current_cells = [start]
    nb_cells = []
    count = 1
    q = {pos_to_tuple(start): 0}

    loops = width
    if width > 11:
        loops = 13
    for i in range(loops):
        if goal in current_cells:
            break

        for current_cell in current_cells:
            for cell in von_neumann_nb(current_cell, width, height):
                if cell not in exclude and pos_to_tuple(cell) not in q:
                    nb_cells.append(cell)

        if not nb_cells:
            break

        for cell in nb_cells:
            q[pos_to_tuple(cell)] = count

        current_cells = nb_cells
        nb_cells = []
        count += 1

    return q


# recursive
def ts():
    pass


def dijkstra():
    pass


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
