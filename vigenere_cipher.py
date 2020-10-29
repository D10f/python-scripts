#!/usr/bin/env python3

'''
vigenere_cipher.py - The vigenere cipher works similarly to the Caesar cipher in
that is uses addition to encrypt a message. The encryption key is not a fixed
number, instead is a word and each character in it is used to shift the text.
The number of possible combinations increases exponentially based on the length
of the word, or set of characters, chosen for encryption. To hack this cipher,
a brute force attack is not very effective and instead a letter frequency
analysis is required.

USAGE: vigenere_cipher.py [-h] [-e cleartext | -d ciphertext] [-k key] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -e cleartext, --encrypt cleartext
                        encrypts the message using the provided key
  -d ciphertext, --decrypt ciphertext
                        decrypts the message using the provided key
  -t, --test            test the encryption with several random strings and
                        keys
  -k key, --key key     key value to used for encryption and decryption
  -v, --verbose         prints additional information to terminal output
  
TODO: Read from and write to files
TODO: Read from stdin, chain with others commands
TODO: Frequency analysis to decrypt a message without the key
'''

import argparse
import logging
import random
import sys
import os

LETTERS='ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def main():
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(args)

    if args.encrypt:
        logging.debug('Encrypting...')
        ciphertext = encrypt(args.encrypt, args.key)
        print(ciphertext)

    if args.decrypt:
        logging.debug('Decrypting...')
        cleartext = decrypt(args.decrypt, args.key)
        print(cleartext)
    
    if args.test:
        logging.debug('Testing...')
        run_tests()


def encrypt(cleartext, key):
    '''Encrypts a message with the key provided.'''

    if key is None:
        print('Encryption error: key not found')
        sys.exit()
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

    # The index of the key will rotate, starting at 0
    key_idx = 0
    transformed_message = []

    for letter in message:
        if letter.upper() in LETTERS:

            letter_idx = LETTERS.find(letter.upper())

            if operation == 'encrypt':
                letter_idx += LETTERS.find(key[key_idx])
            if operation == 'decrypt':
                letter_idx -= LETTERS.find(key[key_idx])

            # Handle any wrap-arounds:
            letter_idx = letter_idx % len(LETTERS)

            # Find the enciphered letter
            enciphered = LETTERS[letter_idx]

            # Determine if letter was upper or lowercase:
            if letter.islower():
                enciphered = enciphered.lower()

            # Add enciphered letter to the output message
            transformed_message.append(enciphered)

            # Rotate the subkey on each iteration
            key_idx += 1 if key_idx == (len(key) - 1) else 0

        else:
            # any non letter-characters remain the same
            transformed_message.append(letter)

    return ''.join(transformed_message)


def run_tests():

    '''Creates long pseudo-random strings and tests the encryption/decryption'''

    logging.debug(f'Testing...')
    SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    # Set random seed to a predictable number for consistent results
    random.seed(42)

    for i in range(20):
        # Create long string of scrambled letters
        sample = SYMBOLS * random.randint(0, 100)
        sample = list(sample)
        random.shuffle(sample)
        sample = ''.join(sample)

        # Creates a 20-letter random key
        key = ''.join([LETTERS[random.randint(0, 25)] for _ in range(20)])

        # Encrypt and decrypt right back
        ciphertext = transform_message(sample, key, 'encrypt')
        cleartext = transform_message(ciphertext, key, 'decrypt')

        # Exit if test didn't pass
        if cleartext != sample:
            logging.debug(f'Expected: {sample[:30].rjust(50, ".")}')
            logging.debug(f'Received: {cleartext[:30].rjust(50, ".")}')
            print('Test Failed!')
            sys.exit()

    print('[OK] All tests passed!')


def parse_arguments():
    parser = argparse.ArgumentParser()
    operations = parser.add_mutually_exclusive_group()

    operations.add_argument('-e', '--encrypt',
        help='encrypts the message using the provided key',
        metavar='cleartext'
    )
    operations.add_argument('-d', '--decrypt',
        help='decrypts the message using the provided key',
        metavar='ciphertext'
    )
    operations.add_argument('-t', '--test',
        help='test the encryption with several random strings and keys',
        action='store_true'
    )
    parser.add_argument('-k', '--key',
        help='key value to used for encryption and decryption',
        metavar='key',
        type=str.upper,
        default=None
    )
    parser.add_argument('-v', '--verbose',
        help='prints additional information to terminal output',
        action='store_true'
    )

    return parser.parse_args()

if __name__ == '__main__':
    main()
