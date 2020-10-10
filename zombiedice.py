#!/usr/bin/python3

import random, sys
from functools import reduce

last_round = False

def main():
    '''Initializes the game by creating a list of all zombie bots'''

    zombies = [
        new_zombie('Alice', dull),
        new_zombie('Bob', bright),
        new_zombie('Charlie', hungry),
        new_zombie('Diana', wanna_be),
        new_zombie('Eric', honest),
        new_zombie('Ferdinand', liar),
        new_zombie('Grace', coward),
        new_zombie('Horacio', cautious),
        new_zombie('Irvine', brave),
        new_zombie('Jake', hunter),
        new_zombie('Kate', greedy),
        new_zombie('Laura', mad),
        new_zombie('Mara', unpredictable),
        new_zombie('Natasha', insecure)
    ]

    # Main game loop, condition only changes after a zombie reaches 13 points
    while not last_round:
        for zombie in zombies:
            play_turn(zombie)

    winner = compare_scores(zombies)
    print(f'{winner["name"]} won in {winner["state"]["rounds"]} rounds!'.upper())
    sys.exit()

def play_turn(zombie):
    '''Contains the core logic functionality of the game and runs once per turn.

    Arguments:
    zombie -- an individual zombie object

    The rules of Zombiedice are: each round the zombie rolls exactly 3 dice
    and sets aside any "shotguns" and "brains" result. The zombie then decides
    whether to pass it's turn and receive a point per "brain", or roll again.
    If the zombie receives three shotguns it will end its turn immediately and
    discard any brains accumulated thus far, in a "push your luck" fashion. All
    "footsteps" results are re-rolled each round.

    When a zombie reaches 13 points after its turn, all zombies left this round
    will play a final turn so that they can catch up (all zombies play the same
    number of rounds). Whoever got the highest score wins. In the event of ties,
    those zombies continue playing until one finally wins.
    '''
    global last_round
    while True:
        # Players roll exactly 3 dices each time, no more no less. After enough
        # rounds there may be fewer than that left (there are 13 dices total)
        dices = dice_left(zombie['state'])
        if dices < 3:
            break

        # The results from the roll are added to the zombie's state
        for result in roll_dice(dices):
            zombie['state'][result] += 1
            print(f"{zombie['name']} rolled {result}")

        # If zombie got shot 3 times round is over
        if zombie['state']['shotguns'] >= 3:
            reset_state(zombie)
            return

        # The zombie's strategy will decide to continue for another round
        if zombie['strategy']() == True:
            break

        # "footsteps" results rolled are re-rolled every time. This could be
        # left out but some of the bot's strategies rely on this value being
        # reset every time.
        zombie['state']['footsteps'] = 0

    # The zombie decided to pass and the score count goes up by 1 per brain
    zombie['state']['score'] = zombie['state']['brains']
    reset_state(zombie)

    # If the zombie's score went up to 13 or higher set the last round
    # to True. All other zombies left in this round get to play one last turn.
    if not last_round and zombie['state']['score'] >= 13:
        last_round = True
        print(f"{zombie['name']} has 13 points, FINAL ROUND!")


def compare_scores(zombies):
    '''Returns the zombie with the highest score

    Arguments:
    zombies -- a list of all the zombies playing'''

    def highest_score(highest, current):
        new_record = highest['state']['score'] < current['state']['score']
        return current if new_record else highest

    return reduce(highest_score, zombies)

def reset_state(zombie):
    '''Resets the state of the zombie for the next round.

    Arguments:
    zombie -- the zombie object with a state property.

    All dice are returned to the "cup" for the next player, effectively setting
    the results for this round back to zero. The number of rounds goes up by 1.'''

    zombie['state']['brains'] = 0
    zombie['state']['shotguns'] = 0
    zombie['state']['footsteps'] = 0
    zombie['state']['rounds'] += 1

def new_zombie(name, personality):
    '''Creates a new zombie bot instance.

    Arguments:
    name -- the name of the zombie
    personality -- a function defining the behavior of the zombie bot

    Each zombie has a name and a strategy function that returns True or False,
    to decide when to continue playing for another round or pass. The internal
    state is reset on every round (except for "rounds" and "score") and is
    passed in as the argument for the strategy, computed based on how the
    current round is going.'''

    state = {
        'shotguns': 0,
        'brains': 0,
        'footsteps': 0,
        'score': 0,
        'rounds': 0
    }

    return {
        'name': name,
        'state': state,
        'strategy': lambda: personality(state)
    }

def roll_dice(n):
    '''Returns a tuple with the results of the roll.

    Arguments:
    n -- the number of dice that will be roll at a time.

    As per the game rules a player must roll exactly 3 dices every time, no more
    no less. Therefore the argument n is only used to know whether the returned
    value should be an empty tuple.'''
    if n < 3:
        return ()

    # Distributed evenly
    SIDES = ['shotguns', 'brains', 'footsteps']
    results = SIDES[random.randint(0,2)] for roll in range(3)]

    return tuple(results)


def dice_left(state):
    '''Returns the number of dice left in the "cup".

    Arguments:
    state -- the zombie's state dictionary.

    The total number of dice is 13 and on each round "shotgun" and "brain"
    results as set aside until the round ends, reducing the number of dice that
    are available for the next roll. This function calculates the result based
    on the zombie's internal state.
    '''
    TOTAL_DICE = 13
    return TOTAL_DICE - (state['shotguns'] + state['brains'])


#   These are all the different strategy functions that define the behavior
#   of the zombie bot dynamically based on it's inner current state. Using
#   composition makes creating more strategies really easy and extensible.
hungry          = lambda state: dice_left(state) < 3
dull            = lambda state: dice_left(state) < 4
bright          = lambda state: dice_left(state) < 6
wanna_be        = lambda state: state['score'] < dice_left(state)
honest          = lambda state: True
liar            = lambda state: False
coward          = lambda state: state['footsteps'] > 0
cautious        = lambda state: state['shotguns'] >= 1
brave           = lambda state: state['shotguns'] == 2
hunter          = lambda state: state['brains'] >= 4
greedy          = lambda state: state['brains'] >= 6
mad             = lambda state: state['brains'] >= 8
unpredictable   = lambda state: random.randint(0,1) == 0
insecure        = lambda state: random.randint(0,2) == 0

if __name__ == '__main__':
    main()
