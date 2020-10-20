#!/usr/bin/python3

'''
affine.py - the affine cipher is a substitution cipher that combines addition
and multiplication.

USAGE: affine_cipher.py [encrypt|decrypt|test|force] [msg] [key]

TODO: read from stdin, write to stdout
TODO: read from file, write to file
'''

from is_lang import is_english
import cryptomath
import argparse
import logging
import random
import sys

SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+[]'
SYMBOL_LEN = len(SYMBOLS)

def main():
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(f'Arguments are: {args}')

    if args.encrypt:
        logging.debug('Encrypting...')
        ciphertext = encrypt(args.encrypt, args.key)
        print(ciphertext)

    if args.decrypt:
        logging.debug('Decrypting...')
        cleartext = decrypt(args.decrypt, args.key)
        print(cleartext)

    if args.force:
        logging.debug(f'Starting brute force attack...')
        brute_force(args.force)

    if args.test:
        logging.debug(f'Running {args.test} tests...')
        run_tests(args.test)


def encrypt(cleartext, key):

    '''
    Encrypts a file using two keys, one to perform multiplication and another
    to perform addition.
    '''

    # Generate a valid, random key for encryption if one was not provided
    if key is None:
        keys = generate_keys()
        print(f'The encryption key is: {keys[2]}')
    else:
        keys = validate_key(int(key))
        if keys is None:
            print('Encryption Error: invalid key')
            print('Usage: affine_cipher.py [--encrypt MESSAGE] [--key NUMBER]')
            print('Leave the key option empty to auto-generate one for you')
            sys.exit()

    ciphertext = ''

    for char in cleartext:
        if char in SYMBOLS:
            # Get the index of the char within the symbol set
            idx = SYMBOLS.find(char)

            # Multiply it by the first key
            idx = idx * keys[0]

            # Add the second key to that
            idx = idx + keys[1]

            # If needed, mod the result by the length of the symbol set
            idx = idx % SYMBOL_LEN

            ciphertext += SYMBOLS[idx]
        else:
            ciphertext += char
    return ciphertext


def decrypt(ciphertext, key):

    '''
    Decrypts a message using the keys provided. It uses the Euclid's algorithm
    to calculate the modular inverse of key_a in order to decrypt the message.
    '''

    # If key was not provided at command line
    if key is None:
        print('Decryption Error: Key is not provided')
        sys.exit()

    # always verify the key is valid for the affine cipher
    keys = validate_key(int(key))
    if keys is None:
        print('Decryption Error: Invalid key')
        sys.exit()

    cleartext = ''

    # get modular inverse of key_a (this will be the decryption key)
    mod_inverse = cryptomath.find_mod_inverse(keys[0], SYMBOL_LEN)
    if mod_inverse is None:
        print('Decryption Error: Provided keys are not coprimes')
        sys.exit()

    for char in ciphertext:
        if char in SYMBOLS:
            # Get the index of the char within the symbol set
            idx = SYMBOLS.find(char)

            # Subtract from it the value of the second key, wrap if needed
            idx = idx - keys[1]
            if idx < 0:
                idx = idx + SYMBOL_LEN

            # Multiply it by the mod inverse of the key_a
            idx = idx * mod_inverse

            # If needed, mod the result by the length of the symbol set
            idx = idx % SYMBOL_LEN

            cleartext += SYMBOLS[idx]
        else:
            cleartext += char
    return cleartext


def validate_key(key):
    '''Validates the provided key works with the aphine cipher'''

    key_a = key // SYMBOL_LEN
    key_b = key % SYMBOL_LEN

    # If keys aren't secure to use with the affine cipher return None
    if cryptomath.gcd(key_a, SYMBOL_LEN) != 1 \
    or (key_a < 0 or key_b < 0) \
    or (key_a <= 1 or key_b <= 1):
        return None
    return (key_a, key_b)


def generate_keys():
    '''Generates a random key and validates it works with the aphine cipher.'''

    while True:
        rand_key = random.randint(2, SYMBOL_LEN ** 2)
        keys = validate_key(rand_key)
        if keys is not None:
            return (keys[0], keys[1], rand_key)


def run_tests(tests):
    '''Tests the encrypt/decrypt functionality with random strings of text'''

    # reset random seed for consistent testing
    random.seed(42)

    for test in range(tests):
        # get a random key
        keys = generate_keys()

        # generate random strings
        sample = SYMBOLS * random.randint(10, 100)
        sample = list(sample)
        random.shuffle(sample)
        sample = ''.join(sample)

        logging.debug(f"Running test #{test:02}: {long_print(sample, 50)}")
        logging.debug(f'Key A: {keys[0]}')
        logging.debug(f'Key B: {keys[1]}')

        # encrypt and decrypt right back
        ciphertext = encrypt(sample, keys[2])
        cleartext = decrypt(ciphertext, keys[2])

        if cleartext != sample:
            print('[ERROR] Test failed!')
            print(f'Expected: {long_print(sample, 40)}')
            print(f'Received: {long_print(cleartext, 40)}')
            sys.exit()

    print('-' * 20)
    print('[OK] All tests passed!')
    print('-' * 20)


def brute_force(ciphertext):
    '''Runs through all possible key combinations and prompts to the user any
    potential matches for confirmation'''

    for i in range(1, SYMBOL_LEN ** 2):
        logging.debug(f'Attack #{i:02}')

        # skip if is not a valid key combination
        keys = validate_key(i)
        if keys is None:
            continue

        cleartext = decrypt(ciphertext, i)
        if is_english(cleartext):
            print('Possible match found:')
            print('-' * 20)
            print(cleartext)
            print('-' * 20)
            response = input('Continue attack? (y/n)\t')
            if response.lower().startswith('n'):
                print('Exiting...')
                sys.exit()
    print('Reached the end of the program!')


def long_print(text, width, sep='.'):

    '''Adds a nicer format for long outputs. Works best with ~30 char upwards'''

    output = text[:width]
    output += f'({len(text) - width} more characters)'.rjust(width, sep)
    return output


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='''affine-cipher.py - encrypt and decrypt messages providing
        a numeric key. If the key is not strong enough it will prompt to enter a
        different one. Alternatively, leave the key option empty while encrypting
        and the program will choose one automatically.'''
    )

    operations = parser.add_mutually_exclusive_group()
    operations.add_argument('-e', '--encrypt',
        help='encrypts the message using the provided key',
        metavar='cleartext'
    )
    operations.add_argument('-d', '--decrypt',
        help='decrypts the message using the provided key',
        metavar='ciphertext'
    )
    operations.add_argument('-f', '--brute-force',
        help='Brute forces over all possible key combinations',
        metavar='ciphertext',
        dest='force'
    )
    operations.add_argument('-t', '--test',
        help='generates random strings to test the encrypt/decrypt functions',
        metavar='number',
        nargs='?',
        const=20,
        type=int
    )
    parser.add_argument('-k', '--key',
        help='key value to used for encryption and decryption',
        metavar='num',
        default=None
    )
    parser.add_argument('-v', '--verbose',
        help='prints additional information to terminal output',
        action='store_true'
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
