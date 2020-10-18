#!/usr/bin/python3

'''transposition.py - an encryption cipher that works by placing each character
in a grid of varying size, and reconstructing the ciphertext in order from the
resulting grid.

USAGE: transposition-cipher.py [encrypt|decrypt|derive|force] [message] [key]

# TODO: add option to read from stdin
# TODO: add option to read from and write to file
'''

import argparse
import logging
import sys

def main():
    args = parse_arguments()

    # Determines the amount of output
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # Perform an operation based on the arguments passed in
    if args.encrypt:
        ciphertext = encrypt(args.encrypt[0], args.encrypt[1])
        print(ciphertext)

    if args.decrypt:
        cleartext = decrypt(args.decrypt[0], args.decrypt[1])
        print(cleartext)

    if args.derive:
        key = derive_key(args.derive[0], args.derive[1])
        print(key)

    if args.force:
        brute_force(args.force)


def encrypt(msg, key, debug=True):

    '''Encrypts a message using the provided key'''

    try:
        # Convert to int and ensure a value gt 0 is passed
        key = int(key)
        if key < 0:
            raise ValueError

        # For debugging purposes...
        if debug:
            logging.debug('Encrypting...')

        ciphertext = ''
        msg_length = len(msg)

        # loop through the message and increase counter by the size of the key
        for col in range(key):
            for char in range(col, msg_length, key):
                ciphertext += msg[char]
        return ciphertext

    except ValueError:
        print('Encryption error: key must be a positive number')


def decrypt(msg, key, debug=True):

    '''Decrypts a message using the provided key'''

    try:
        # Convert to int and ensure a value gt 0 is passed
        key = int(key)
        if key < 0:
            raise ValueError

        # For debugging purposes...
        if debug:
            logging.debug('Decrypting...')

        msg_length = len(msg)
        cleartext = [''] * msg_length

        # loop through the message and increase counter by the size of the key
        # use an out of loop index to keep track of current letter of cleartext
        idx = 0
        for i in range(key):
            for col in range(i, msg_length, key):
                cleartext[col] = msg[idx]
                idx += 1
        return ''.join(cleartext)

    except ValueError:
            print('Encryption error: key must be a positive number')


def derive_key(cleartext, ciphertext):

    '''Calculates the key used to encrypt a message from it's cleartext form'''

    logging.debug('Deriving key...')

    # The number of combinations is limited by the size of the original text
    permutations = len(cleartext)

    # Loop through all possible permutations until a match is found
    for key in range(1, permutations):
        result = encrypt(cleartext, key, debug=False)
        if result == ciphertext:
            return key

    # If no match is found, the messages are not encrypted with the same cipher
    print('Match error: The messages are not encrypted using the same cipher')
    logging.info(f'({permutations}) permutations tried...')
    sys.exit()


def brute_force(ciphertext):

    '''Brute forces through all possible key permutations. Prints results to
    terminal output in blocks of 10 to avoid cluttering the terminal'''

    logging.debug('Starting brute force attack...')

    permutations = len(ciphertext)
    for i in range(1, permutations):
        result = decrypt(ciphertext, i, debug=False)
        print(i, result, sep=': ')

        if i != permutations and i % 10 == 0:
            print('-' * 10)
            response = input('Printing 10 results, continue? ')
            print('-' * 10)
            if 'n' in response.lower():
                print('Exiting...')
                sys.exit()


def parse_arguments():
    parser = argparse.ArgumentParser()
    operations = parser.add_mutually_exclusive_group()

    operations.add_argument('-e', '--encrypt',
        help='encrypts a message using the provided key',
        metavar=('msg', 'key'),
        nargs=2
    )
    operations.add_argument('-d', '--decrypt',
        help='decrypts a message using the provided key',
        metavar=('msg', 'key'),
        nargs=2
    )
    operations.add_argument('-k', '--derive-key',
        help='calculates the key used to encrypt a message',
        dest='derive',
        metavar=('cleartext', 'ciphertext'),
        nargs=2
    )
    operations.add_argument('-f', '--brute-force',
        help='prints all possible combinations to terminal output',
        metavar='msg',
        dest='force'
    )
    parser.add_argument('-v', '--verbose',
        help='prints additional information to terminal output',
        action='store_true'
    )

    return parser.parse_args()

if __name__ == '__main__':
    main()
