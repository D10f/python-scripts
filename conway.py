#!/usr/bin/python3

'''
conway.py - plays "The Game Of Life" autonomously and prints each generation
to the terminal output.
'''

import random
import time
import copy

def main():
    generation = init()
    while True:
        draw(generation)
        procreate(generation)
        time.sleep(1)


def init():
    '''Initializes the game - places cells in the board at random positions'''

    width = 20
    height = 30
    generation = []

    for x in range(width):
        column = []
        for y in range(height):
            cell_state = random.randint(0,1)
            cell = '#' if cell_state == 0 else ' '
            column.append(cell)
        generation.append(column)

    return generation


def draw(generation):
    '''Draws the current generation of cells to the screen'''

    width = len(generation)
    height = len(generation[0])

    for x in range(width):
        for y in range(height):
            print(generation[x][y], end=' ')
        print()

    print('-' * width)

def procreate(generation):
    '''Calculates the next generation of cells'''

    width = len(generation)
    height = len(generation[0])

    next_generation = copy.deepcopy(generation)

    for x in range(width):
        for y in range(height):

            # Get coordinates for neighbour cells (relative to current cell)
            left  = (x - 1) % width
            right = (x + 1) % width
            top   = (y - 1) % height
            bot   = (y + 1) % height

            # Count how many neighbour cells are alive
            alive_neighbours = 0
            if next_generation[left][top] == '#':
                alive_neighbours += 1

            if next_generation[x][top] == '#':
                alive_neighbours += 1

            if next_generation[right][top] == '#':
                alive_neighbours += 1

            if next_generation[left][y] == '#':
                alive_neighbours += 1

            if next_generation[right][y] == '#':
                alive_neighbours += 1

            if next_generation[left][bot] == '#':
                alive_neighbours += 1

            if next_generation[x][bot] == '#':
                alive_neighbours += 1

            if next_generation[right][bot] == '#':
                alive_neighbours += 1

            # Apply the rules of the game
            if next_generation[x][y] == '#' and (alive_neighbours == 2 or alive_neighbours == 3):
                generation[x][y] = '#'
            elif next_generation[x][y] == ' ' and alive_neighbours == 3:
                generation[x][y] = '#'
            else:
                generation[x][y] = ' '


if __name__ == '__main__':
    main()
