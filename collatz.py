#!/usr/bin/env python3

'''
Collatz sequence starts with any positive integer n; if it's even is divided by
2 and if it's odd it will be multiplied by 3 and then plus 1. This sequence is
repeated until, eventually and invariable, n becomes 1.

USAGE: collatz.py NUMBER
'''

import argparse
import logging
import random
import time


def main():
    args = parse_arguments()

    logging.basicConfig(level=logging.DEBUG)
    logging.debug(args)

    logging.debug(f'Starting number: {args.number}')
    start = time.time()
    collatz_sequence(args.number)
    print(f'Finished in {round(time.time() - start, 2)} seconds')


def collatz_sequence(n):
    print(f'Current number is {n}')

    # Create an artificial delay for a more "interesting" output
    time.sleep(0.2)

    if n == 1:
        print('End of sequence')
        return True
    if n % 2 == 0:
        return collatz_sequence(n // 2)
    else:
        return collatz_sequence((3 * n) + 1)


def parse_arguments():
    parser = argparse.ArgumentParser()

    # strings will convert to integers and turned into absolute value 
    parser.add_argument('number',
        help='Any positive integer',
        type=lambda x: abs(int(x)),
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
