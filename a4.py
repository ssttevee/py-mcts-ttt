import random
from functools import reduce
from itertools import count
from datetime import datetime, timedelta


all_win_conds = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [6, 4, 2],
]


win_cond_map = {
    i: list(filter(lambda cond: i in cond, all_win_conds)) for i in range(9)
}


class Game:
    def __init__(self, board=None, turn='x'):
        self.__board = board or ['']*9
        self.__turn = turn

    def current_turn(self):
        return self.__turn

    def state(self):
        return ''.join(map(lambda x: x or '_', self.__board))

    def valid_moves(self):
        return map(lambda i: self.__cell(i), filter(lambda i: not self.__board[i], range(9)))

    def clone(self):
        return Game(self.__board.copy(), self.__turn)

    def __check_index_win(self, index, player):
        return self.__check_win(win_cond_map[index], player)

    def __check_win(self, conds, player):
        return any(map(lambda cond: all(map(lambda i: self.__board[i] == player, cond)), conds))

    def is_no_more_moves(self):
        return all(self.__board)

    def move(self, cell):
        index = int(cell) - 1
        if not (0 <= index <= 8) or self.__board[index]:
            raise Exception('bad move')

        self.__board[index] = self.__turn

        try:
            return self.__check_index_win(index, self.__turn)
        finally:
            self.__turn = 'x' if self.__turn == 'o' else 'o'

    def __cell(self, index):
        return self.__board[index] or str(1 + index)

    def __print_row(self, y):
        print(' ' + ' | '.join(self.__cell(i + 3*y) for i in range(3)) + ' ')

    def print(self):
        self.__print_row(0)
        print('---+---+---')
        self.__print_row(1)
        print('---+---+---')
        self.__print_row(2)


def winrate(record):
    if not record[1]:
        return 0.5
    return record[0] / record[1]


class MonteCarlo:
    def __init__(self):
        self.__memory = {}

    def next_move(self, state):
        records = self.__memory[state]
        return reduce(
            lambda a, b: a if winrate(records[a]) > winrate(records[b]) else b,
            records.keys(),
        )

    def __pick_move(self, state):
        records = self.__memory[state]
        return random.choices(
            list(records.keys()),
            list(map(winrate, records.values())),
        )[0]

    def __simulate(self, game):
        # whoami
        me = game.current_turn()

        # keep track of moves made
        my_moves = []
        their_moves = []

        # play game
        i_won = None
        while not game.is_no_more_moves():
            current_state = game.state()
            if current_state not in self.__memory:
                self.__memory[current_state] = {
                    move: (0, 0) for move in game.valid_moves()
                }

            move = self.__pick_move(current_state)

            # take note of who made what move
            is_me = game.current_turn() == me
            if is_me:
                my_moves.append((current_state, move))
            else:
                their_moves.append((current_state, move))

            if game.move(move):
                i_won = True if is_me else False
                break

        # determine score
        if i_won is None:
            scores = (0, 0)
        elif i_won:
            scores = (1, -1)
        else:
            scores = (-1, 1)

        # update memory
        for i, (state, move) in zip(range(len(my_moves)), reversed(my_moves)):
            self.__memory[state][move] = (
                self.__memory[state][move][0] + .5 +
                (scores[0] * 0.5 / (i + 1)),
                self.__memory[state][move][1] + 1,
            )

        for i, (state, move) in zip(range(len(their_moves)), reversed(their_moves)):
            self.__memory[state][move] = (
                self.__memory[state][move][0] + .5 +
                (scores[1] * 0.5 / (i + 1)),
                self.__memory[state][move][1] + 1,
            )

    def think(self, game, time_limit):
        end_time = datetime.now() + time_limit
        while True:
            self.__simulate(game.clone())

            if datetime.now() > end_time:
                break


def clear():
    print('\033[H\033[J', end='')


def play_a_new_game():
    clear()

    done = False
    win = None
    bot = MonteCarlo()
    g = Game()
    for i in count():
        if i % 2:
            print('thinking...')

            bot.think(g, timedelta(milliseconds=100))
            if g.move(bot.next_move(g.state())):
                win = False

        else:
            while not done:
                g.print()
                try:
                    if g.move(input('What\'s your move? [' + ','.join(g.valid_moves()) + ']: ')):
                        win = True

                    done = True
                except ValueError:
                    clear()
                    print('Invalid input')
                except KeyboardInterrupt:
                    print()
                    return
                except Exception as e:
                    if str(e) == 'bad move':
                        clear()
                        print('Invalid move')
                    else:
                        raise e
            else:
                done = False

        clear()

        if win is not None or g.is_no_more_moves():
            break

    g.print()

    if win is None:
        print('It\'s a tie!')
    elif win:
        print('You win!')
    else:
        print('You lose!')


if __name__ == '__main__':
    play_a_new_game()
