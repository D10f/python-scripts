#!/usr/bin/python3

'''
caesar.py - a simple implementation of the caesar cipher used over 2000 years
ago.

USAGE: caesar.py [encrypt|decrypt|derive|force] [message] [key]

# TODO: accept input from stdin in order to pipe commands together
# TODO: accept text files as input, and redirect output to files
'''

import argparse
import logging
import sys

def main():
    args = parse_arguments()

    # Creates more output
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+'

    # Perform a different operation based on the arguments passed in
    if args.encrypt:
        ciphertext = encrypt_msg(args.encrypt[0], args.encrypt[1], SYMBOLS)
        logging.debug(f'Encryption finished!')
        print(ciphertext)

    if args.decrypt:
        cleartext = decrypt_msg(args.decrypt[0], args.decrypt[1], SYMBOLS)
        logging.debug(f'Decryption finished!')
        print(cleartext)

    if args.derive_key:
        key = derive_key(args.derive_key[0], args.derive_key[1], SYMBOLS)
        if key:
            print(f'The key used to encrypt this message was {key}')

    if args.force:
        brute_force(args.force, SYMBOLS)


def encrypt_msg(msg, key, symbols, debug=True):
    try:
        key = int(key)
        wrapper_value = len(symbols)
        ciphertext = ''

        # The debug keyword here is used to omit this logging statement
        # because the derive_key funciton will call it, creating a ton of
        # unnecessary output
        if debug:
            logging.debug('Starting encryption...')
        for char in msg:
            # Find out if the letter can be encrypted
            if char in symbols:
                idx = symbols.find(char)
                idx = idx + key

                # Wrap values where index is under or over the symbols list
                if idx >= wrapper_value:
                    idx = idx - wrapper_value
                elif idx < 0:
                    idx = idx + wrapper_value

                # Append the symbol at calculated index
                ciphertext += symbols[idx]
            else:
                # Append current character as is
                if char != ' ':
                    logging.debug(f'Character {char} not within symbols list')
                ciphertext += char

        return ciphertext

    except ValueError:
        print(f'Encryption error: Invalid argument {key} is not a number')
        sys.exit()


def decrypt_msg(msg, key, symbols, debug=True):
    try:
        key = int(key)
        wrapper_value = len(symbols)
        cleartext = ''

        # The debug keyword here is used to omit this logging statement
        # because the brute_force funciton will call it, creating a ton of
        # unnecessary output
        if debug:
            logging.debug('Starting decryption...')
        for char in msg:
            # Find out if the char can be encrypted or append as is
            if char in symbols:
                idx = symbols.find(char)
                idx = idx - key

                # Wrap values where new char is under or over the symbols list
                if idx >= wrapper_value:
                    idx = idx - wrapper_value
                elif idx < 0:
                    idx = idx + wrapper_value

                # Append the symbol at calculated index
                cleartext += symbols[idx]
            else:
                # Append current character as is
                if char != ' ':
                    logging.debug(f'Character {char} not within symbols list')
                cleartext += char

        return cleartext

    except ValueError:
        print(f'Decryption error: Invalid argument {key} is not a number')
        sys.exit()


def derive_key(cleartext, ciphertext, symbols):
    logging.debug('Starting derivation of key...')
    for i in range(len(symbols)):
        # Encrypt the cleartext until a match is found
        result = encrypt_msg(cleartext, i, symbols, debug=False)
        if result == ciphertext:
            return i
            
    print("These messages don't match or don't share the same cipher codes")


def brute_force(ciphertext, symbols):
    logging.debug('Starting brute force attack...')
    for i in range(len(symbols)):
        print(decrypt_msg(ciphertext, i, symbols, debug=False))


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
    parser.add_argument('-v', '--verbose',
        help='prints additional information to terminal output',
        dest='verbose',
        action='count'
    )

    return parser.parse_args()


if __name__ == '__main__':
    main()
