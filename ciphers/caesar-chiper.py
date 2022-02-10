#!/usr/bin/python3

'''
caesar.py - a simple implementation of the caesar cipher used over 2000 years
ago. You can use this script to encrypt or decrypt a message, derive the key
that was used to encrypt a message, brute force any message encrypted using
this cipher and run test to verify it works

USAGE: caesar-cipher.py [encrypt|decrypt|derive|force|test] [message] [key]

# TODO: accept input from stdin in order to pipe commands together
# TODO: accept text files as input, and write output to files
'''

from is_lang import is_english
import argparse
import logging
import random
import copy
import sys

def main():
    args = parse_arguments()

    # Creates more output
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+'

    # Perform a different operation based on the arguments passed in
    if args.encrypt:
        ciphertext = encrypt(args.encrypt[0], args.encrypt[1])
        logging.debug(f'Encryption finished!')
        print(ciphertext)

    if args.decrypt:
        cleartext = decrypt(args.decrypt[0], args.decrypt[1])
        logging.debug(f'Decryption finished!')
        print(cleartext)

    if args.derive_key:
        key = derive_key(args.derive_key[0], args.derive_key[1])
        if key:
            print(f'The key used to encrypt this message was {key}')

    if args.force:
        brute_force(args.force)

    if args.test:
        run_test(args.test)


def encrypt(msg, key, debug=True):

    '''Encrypts a message using the provided key'''

    # avoids unnecessary calls from derive key calls
    if debug:
        logging.debug('Starting encryption...')
    SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+'

    try:
        key = int(key)
        wrapper_value = len(SYMBOLS)
        ciphertext = ''

        for char in msg:
            # Find out if the letter can be encrypted
            if char in SYMBOLS:
                idx = SYMBOLS.find(char)
                idx = idx + key

                # Wrap values where index is under or over the symbols list
                if idx >= wrapper_value:
                    idx = idx - wrapper_value
                elif idx < 0:
                    idx = idx + wrapper_value

                # Append the symbol at calculated index
                ciphertext += SYMBOLS[idx]
            else:
                # Append current character as is
                if char != ' ':
                    logging.debug(f'Character {char} not within symbols list')
                ciphertext += char

        return ciphertext

    except ValueError:
        print(f'Encryption error: Invalid argument {key} is not a number')
        sys.exit()


def decrypt(msg, key, debug=True):

    '''Decrypts a message using the provided key'''

    # avoids unnecessary calls from derive key calls
    if debug:
        logging.debug('Starting decryption...')
    SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+'

    try:
        key = int(key)
        wrapper_value = len(SYMBOLS)
        cleartext = ''

        for char in msg:
            # Find out if the char can be encrypted or append as is
            if char in SYMBOLS:
                idx = SYMBOLS.find(char)
                idx = idx - key

                # Wrap values where new char is under or over the symbols list
                if idx >= wrapper_value:
                    idx = idx - wrapper_value
                elif idx < 0:
                    idx = idx + wrapper_value

                # Append the symbol at calculated index
                cleartext += SYMBOLS[idx]
            else:
                # Append current character as is
                if char != ' ':
                    logging.debug(f'Character {char} not within symbols list')
                cleartext += char

        return cleartext

    except ValueError:
        print(f'Decryption error: Invalid argument {key} is not a number')
        sys.exit()


def derive_key(cleartext, ciphertext):

    '''Calculates the key used to encrypt a message from it's cleartext form'''

    logging.debug('Starting derivation of key...')
    SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+'

    for i in range(len(SYMBOLS)):
        result = encrypt(cleartext, i, debug=False)
        if result == ciphertext:
            return i

    print("These messages don't match or don't share the same cipher codes")


def brute_force(ciphertext):

    '''Brute forces through all possible key values to decrypt the message. On
    each pass it evaluates if the decrypted string is in English and print it
    to the terminal output for confirmation'''

    logging.debug('Starting brute force attack...')
    SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+'

    try:
        for i in range(len(SYMBOLS)):
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


def run_test(total_tests):

    '''Creates long pseudo-random strings and tests the encryption/decryption'''

    logging.debug(f'Running {total_tests} tests...')
    SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+ '

    # set random seed to static number for consistent, reproducible tests
    random.seed(42)
    for i in range(1, total_tests + 1):
        # generate a significant sample string
        sample = SYMBOLS * random.randint(10, 100)
        sample_length = len(sample)

        # randomize the sorting
        sample = list(sample)
        random.shuffle(sample)
        sample = ''.join(sample)

        # generate random key
        key = random.randint(1, 26)

        # encrypt and decrypt back
        ciphertext = encrypt(sample, key, debug=False)
        decrypted = decrypt(ciphertext, key, debug=False)

        # A little bit of fancy formatting
        # {i:02} prints variable i with a leading 0 if length is not 2
        logging.debug(f"Running test #{i:02}:\t{ciphertext[:40]}" + \
        f"{sample_length - 40} characters".rjust(20, '.'))

        if decrypted != sample:
            print("[ERROR] Test failed! Exiting...")
            logging.debug(f'Expected:\n{sample}')
            logging.debug(f'Got:\n{decrypted}')
            sys.exit()

    print('-' * 50)
    print('[OK] All tests passed!')
    print('-' * 50)


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
        help='derives the encryption key, provided a cleartext and a ciphertext',
        metavar=('cleartext', 'ciphertext'),
        nargs=2
    )
    operations.add_argument('-f', '--force',
        help='brute forces through all possible key values to decrypt a message',
        dest='force',
        metavar='msg'
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
        dest='verbose',
        action='count'
    )

    return parser.parse_args()


if __name__ == '__main__':
    main()
