import random
from functools import reduce
from itertools import count
from datetime import datetime, timedelta


class Game:
    def __init__(self, board=None, turn='x'):
        self.__board = board or ['']*9
        self.__turn = turn

    def current_turn(self):
        return self.__turn

    def state(self):
        return ''.join(map(lambda x: x or '_', self.__board))

    def valid_moves(self):
        return list(map(lambda i: self.__cell(i), filter(lambda i: not self.__board[i], range(9))))

    def clone(self):
        return Game(self.__board.copy(), self.__turn)

    def is_tie(self):
        return not self.is_win('x') and not self.is_win('o')

    def is_win(self, player):
        return (player == self.__cell(0) == self.__cell(1) == self.__cell(2)) \
            or (player == self.__cell(3) == self.__cell(4) == self.__cell(5)) \
            or (player == self.__cell(6) == self.__cell(7) == self.__cell(8)) \
            or (player == self.__cell(0) == self.__cell(3) == self.__cell(6)) \
            or (player == self.__cell(1) == self.__cell(4) == self.__cell(7)) \
            or (player == self.__cell(2) == self.__cell(5) == self.__cell(8)) \
            or (player == self.__cell(0) == self.__cell(4) == self.__cell(8)) \
            or (player == self.__cell(6) == self.__cell(4) == self.__cell(2))

    def is_over(self):
        return all(self.__board) \
            or self.is_win('x') \
            or self.is_win('o')

    def move(self, cell):
        cell = int(cell)
        if not (1 <= cell <= 9) or self.__board[cell-1]:
            raise Exception('bad cell')

        self.__board[cell-1] = self.__turn
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
        while not game.is_over():
            current_state = game.state()
            if current_state not in self.__memory:
                self.__memory[current_state] = {
                    move: (0, 0) for move in game.valid_moves()
                }

            move = self.__pick_move(current_state)

            # take note of who made what move
            if game.current_turn() == me:
                my_moves.append((current_state, move))
            else:
                their_moves.append((current_state, move))

            game.move(move)

        # determine score
        if game.is_tie():
            scores = (0, 0)
        elif game.is_win(me):
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
        start_time = datetime.now()
        while True:
            self.__simulate(game.clone())

            if datetime.now() - start_time > time_limit:
                break


def clear():
    print('\033[H\033[J', end='')


def play_a_new_game():
    clear()

    bot = MonteCarlo()
    g = Game()
    while not g.is_over():
        g.print()
        try:
            g.move(input('What\'s your move? [' + ','.join(g.valid_moves()) + ']: '))
            clear()

            if g.is_over():
                break

            print('thinking...')

            bot.think(g, timedelta(milliseconds=100))
            clear()

            g.move(bot.next_move(g.state()))
            continue
        except ValueError:
            clear()
            print('Invalid input')
        except KeyboardInterrupt:
            print()
            return
        except Exception as e:
            if str(e) == 'bad cell':
                clear()
                print('Invalid move')
            else:
                raise e

    g.print()

    if g.is_win('x'):
        print('You win!')
    elif g.is_win('o'):
        print('You lose!')
    else:
        print('It\'s a tie!')


if __name__ == '__main__':
    play_a_new_game()
