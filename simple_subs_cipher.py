#!/usr/bin/python3

'''
simple_sub_cipher.py - An implementation of the "simple substitution cipher"

This cipher works by substituting each letter of a message by another letter
matching the encryption key. The encryption key is not a number like in the
addition or multiplicative ciphers, but a randomly arranged set of characters
(in this case the English alphabet).

Brute force attacks are not effective due to the immense number of possible
key combinations, even for modern computers. Instead, a cross-reference and
frequency analysis can be used to create a map of each letter to its cipher.

Lines 143-246 contains the code to perform such a cross-reference attack.

USAGE: simple_sub_cipher.py [encrypt|decrypt|test|force] [msg] [key]

TODO: Read stdin and write to stdout
TODO: Read from file and write to files
'''

from make_word_pattern import get_word_pattern
from word_patterns import en_patterns
import argparse
import logging
import random
import copy
import re
import sys

LETTERS='ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def main():
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(args)

    if args.encrypt:
        logging.debug('Encrypting...')
        ciphertext = encrypt(args.encrypt, key=args.key)
        print(ciphertext)

    if args.decrypt:
        logging.debug('Decrypting...')
        cleartext = decrypt(args.decrypt, args.key)
        print(cleartext)

    if args.force:
        cleartext = brute_force(args.force)
        print(cleartext)

    if args.test:
        logging.debug(f'Running {args.test} tests...')
        run_tests(args.test)


def encrypt(cleartext, key=None):
    '''Encrypts a message with the key provided. If is not, one will be randomly
    generated and printed to the terminal output'''

    if key is None:
        key = generate_key()
    print(f'The encryption key is: {key}')
    return transform_message(cleartext, key, 'encrypt')


def decrypt(ciphertext, key):
    '''Decrypts a message using the provided key'''
    if key is None:
        print('Decryption error: key not found')
        sys.exit()
    return transform_message(ciphertext, key, 'decrypt')


def transform_message(message, key, operation):
    '''Encrypts or decrypts a message based on the operation specified'''

    logging.debug(f'{operation.title()}ing...')

    # symbol_set means what the current msg is checked against
    # source_set means the source of the new constructed string is
    if operation == 'encrypt':
        symbol_set, source_set = LETTERS, key
    elif operation == 'decrypt':
        symbol_set, source_set = key, LETTERS

    transformed = []

    # simple lookup between provided message and key
    for char in message:
        if char.upper() in symbol_set:
            idx = symbol_set.find(char.upper())
            if char.islower():
                transformed.append(source_set[idx].lower())
            else:
                transformed.append(source_set[idx])
        else:
            transformed.append(char)

    return ''.join(transformed)


def run_tests(tests):
    '''Runs a battery of tests using randomly generated text and keys'''

    # Reset seed for consistent results
    random.seed(42)

    for test in range(1, tests + 1):
        # random sample text
        sample = list(LETTERS * random.randint(10, 100))
        random.shuffle(sample)
        sample = ''.join(sample)

        # create a new encryption key
        key = generate_key()

        # encrypt and decrypt right back
        ciphertext = transform_message(sample, key, 'encrypt')
        cleartext = transform_message(ciphertext, key, 'decrypt')

        # something is wrong if
        if cleartext != sample:
            print(f'Test #{test:02} failed{"[ERROR]".rjust(75, ".")}')
            print(f'Expected: {long_print(sample, 40)}')
            print(f'Received: {long_print(cleartext, 40)}')
            sys.exit()

        # print in nicer format
        logging.debug(f'Running test #{test:02}:{"[OK]".rjust(77, ".")}')

    print('-' * 20)
    print('[OK] All tests passed!')
    print('-' * 20)


def generate_key():
    symbols = list(LETTERS)
    random.shuffle(symbols)
    return ''.join(symbols)


def long_print(text, width, sep='.'):

    '''Adds a nicer format for long outputs. Works best with ~30 char upwards'''

    output = text[:width]
    output += f'({len(text) - width} more characters)'.rjust(width, sep)
    return output


def brute_force(message):
    # Clean up data, remove non-letter characters from message
    cipher_text = remove_non_letters(message).split()

    # Create a blank map for letters as they are deciphered
    cipher_map = create_letter_map()

    # Loop through each word in the message, get a letter pattern to get any
    # potential candidates. Create and return a map with the results
    cipher_map = get_letter_mapping(cipher_map, cipher_text)

    # Reduces the number of possible letters by cross referencing those with
    # only one solution. At this point the map may be fully on partially solved
    reduced_map = get_reduced_map(cipher_map)

    # Based on the reduced map, it produces a decryption key
    key = create_key_from_map(reduced_map)

    return transform_message(message, key, 'decrypt')


def get_letter_mapping(cipher_map, cipher_text):
    _cipher_map = copy.deepcopy(cipher_map)

    for word in cipher_text:
        # Create a blank map for each word
        word_map = create_letter_map()
        word_len = len(word)

        # Get letter pattern, compare it and get similar words from dictionary
        pattern = get_word_pattern(word)
        candidates = en_patterns.get(pattern, None)

        if not candidates:
            logging.debug(f'Candidates not found for {word}')
            continue

        # Go through each candidate's letter, add to the word map
        for candidate in candidates:
            for i in range(word_len):
                if candidate[i] not in word_map[word[i]]:
                    word_map[word[i]].append(candidate[i])

        # Combine every word's new map with global cipher map
        _cipher_map = combine_maps(_cipher_map, word_map)

    return _cipher_map


def combine_maps(map_a, map_b):
    # Use map_a as a start point
    combined_map = copy.deepcopy(map_a)

    for letter in LETTERS:
        # If there's something at B
        if map_b[letter]:
            if not map_a[letter]:
                # If there is nothing at A, copy everything from B
                [combined_map[letter].append(x) for x in map_b[letter]]
            else:
                # If there is something at A and B, get only common letters
                combined_map[letter] = [x for x in map_a[letter] if x in map_b[letter]]

    return combined_map


def get_reduced_map(cipher_map):
    _cipher_map = copy.deepcopy(cipher_map)

    # Letters with only one option are considered solved
    solved_letters = [x[0] for x in _cipher_map.values() if len(x) == 1]

    for s in solved_letters:
        for letter in LETTERS:
            # Remove already solved letters
            if len(_cipher_map[letter]) > 1 and s in _cipher_map[letter]:
                _cipher_map[letter].remove(s)
                # If list length goes down to 1, a new letter is solved
                if len(_cipher_map[letter]) == 1:
                    solved_letters.append(_cipher_map[letter][0])

    return _cipher_map


def create_key_from_map(cipher_map):

    key = ['_'] * len(LETTERS)
    for idx, letter in enumerate(LETTERS):
        if len(cipher_map[letter]) == 1:
            i = LETTERS.find(cipher_map[letter][0])
            key[i] = letter
    return ''.join(key)


def remove_non_letters(msg):
    upper_letters_only = re.compile(r'[^A-Z\s]')
    return upper_letters_only.sub('', msg.upper())


def create_letter_map():
    return { 'A': [], 'B': [], 'C': [], 'D': [], 'E': [], 'F': [], 'G': [], \
    'H': [], 'I': [], 'J': [], 'K': [], 'L': [], 'M': [], 'N': [], 'O': [], \
    'P': [], 'Q': [], 'R': [], 'S': [], 'T': [], 'U': [], 'V': [], 'W': [], \
    'X': [], 'Y': [], 'Z': []}


def parse_arguments():
    parser = argparse.ArgumentParser()

    operations = parser.add_mutually_exclusive_group()
    operations.add_argument('-e', '--encrypt',
        help='Encrypts a message',
        metavar='cleartext'
    )
    operations.add_argument('-d', '--decrypt',
        help='Decrypts a message',
        metavar='ciphertext'
    )
    operations.add_argument('-f', '--brute-force',
        help='Attempts decryption through cross referencing analysis',
        dest='force',
        metavar='msg'
    )
    operations.add_argument('-t', '--test',
        help='Tests the functionality of the encryption and decryption',
        metavar='number',
        nargs='?',
        type=int,
        const=20
    )
    parser.add_argument('-k', '--key',
        help='Key used for encryption. If not provided one will be generated',
        default=None
    )
    parser.add_argument('-v', '--verbose',
        help='prints additional information to terminal output',
        action='store_true'
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
