#!/usr/bin/python3

'''transposition.py - an encryption cipher that works by placing each character
in a grid of varying size, and reconstructing the ciphertext in order from the
resulting grid.

USAGE: transposition-cipher.py [encrypt|decrypt|derive|force|test] [message] [key]

# TODO: add option to read from stdin
# TODO: add option to read from and write to file
'''

from is_lang import is_english
import argparse
import logging
import random
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

    if args.test:
        run_test(args.test)


def encrypt(msg, key, debug=True):

    '''Encrypts a message using the provided key'''

    try:
        # Convert to int and ensure a value gt 0 is passed
        key = int(key)
        if key < 0:
            raise ValueError

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

    '''Brute forces through all possible key values to decrypt the message. On
    each pass it evaluates if the decrypted string is in English and print it
    to the terminal output for confirmation'''

    logging.debug('Starting brute force attack...')
    permutations = len(ciphertext)

    try:
        for i in range(1, permutations):
            result = decrypt(ciphertext, i, debug=False)
            if is_english(result):
                print('Found potential match:', end='\n\n')
                print(result)
                response = input('Continue? (y/n)')
                if response.lower().startswith('n'):
                    raise KeyboardInterrupt

        print('Reached end of text')
    except KeyboardInterrupt:
        print('Exiting program...')
        sys.exit()


def run_test(tests):

    '''Creates long pseudo-random strings and tests the encryption/decryption'''

    # set random seed to static number for consistent, reproducible tests
    random.seed(42)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+ '

    for i in range(1, tests + 1):
        # create a long string of text
        sample = chars * random.randint(10, 100)
        sample_length = len(sample)

        # randomize the input
        sample = list(sample)
        random.shuffle(sample)
        sample = ''.join(sample)

        # random key (for transposition cipher max value is msg length / 2)
        key = random.randint(1, sample_length // 2)

        # encrypt and decrypt right back
        ciphertext = encrypt(sample, key, debug=False)
        decrypted = decrypt(ciphertext, key, debug=False)

        # A little bit of fancy formatting
        # {i:02} prints variable i with a leading 0 if length is not 2
        logging.debug(f"Running test #{i:02}:\t{ciphertext[:40]}" + \
        f"{sample_length - 40} characters".rjust(20, '.'))

        if decrypted != sample:
            print('[ERROR] Test Failed!')
            logging.debug(f'Expected:\n{sample}')
            logging.debug(f'Got:\n{decrypted}')
            sys.exit()

    print('-' * 20)
    print('[OK] All tests passed!')
    print('-' * 20)


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
    operations.add_argument('-t', '--test',
        help='Test batch of 20 randomly generated strings of text',
        metavar='tests',
        nargs='?',
        const=20,
        type=int
    )
    parser.add_argument('-v', '--verbose',
        help='prints additional information to terminal output',
        action='store_true'
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
