#!/usr/bin/env python3

'''
Check passwords against the popular "Have I been Pwned?" website to find out if
it has been seen in any of the recorded data breaches. It does so by leveraging
the website's API to send a only fragment of a hash of the password (not the
password itself) and compare the results for that particular signature.

Provide the passwords you'd like to check as arguments to the script. You may
write as many or as little as you like, however note that commands entered
at the command line are registered in your computer. There are ways of deleting
the history of entered commands in your machine but for better privacy you can
provide a CSV file instead (which you should keep safe or delete afterwards).

This script is intended to work with CSV files exported by the KeePassXC
password manager. This means that the file should contain at least 2 columns
with the headers "Title" and "Password", title being the website or account.

usage: password_checker.py [-h] [-f FILE] [-d [DELETE]] [-v]
                           [passwords [passwords ...]]

positional arguments:
  passwords             A list of passwords to check

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to an existing CSV file containing the passwords
                        to check
  -d [DELETE], --delete [DELETE]
                        If a CSV file is provided, it'll be securely deleted
                        by writing random bytes repeteadly over the original
                        content of the file, before deleting the file from
                        disk. Provide a number of rounds (by default 3) to
                        overwrite the file for extra security.
  -v, --verbose         prints additional information to terminal output
'''

import requests
import argparse
import logging
import hashlib
import pathlib
import secrets
import csv
import os

def main():
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(args)

    if args.file:
        file = args.file[0]

        if (not file.is_file() or file.suffix.lower() != '.csv'):
            print('File not found, please check the filename and path')
            return False

        with open(file) as f:
            dict_file = csv.DictReader(f)
            for row in dict_file:
                title = row['Title']
                password = row['Password']
                logging.debug(f"Checking password for {title}")
                have_i_been_pwned(password, account=title)

        if args.delete:
            logging.debug(f'Securely deleting file ({args.delete} rounds...) ')
            delete_file(file, rounds=args.delete)

    if args.passwords:
        for password in args.passwords:
            have_i_been_pwned(password)


def delete_file(file, rounds=3):
    '''Overwrites the contents of a file with random bytes multiple times and
    deletes the file handle from disk. An attacker examining the disk would
    only be able to recover random gibberish instead of the original content.'''

    file_size = os.path.getsize(file)
    with open(file, 'wb') as f:
        for _ in range(rounds):
            f.write(secrets.token_bytes(file_size))
            f.seek(0)
    os.unlink(file)


def have_i_been_pwned(password, account=None):
    'Checks and prints out to console any matches found for a password'

    head, tail = hash_password(password)
    response = send_request(head)
    match = check_hash(response, tail)

    if not account:
        account = f'{password[:3]}...'

    if (match):
        print(f'Found match for "{account}" {match} times!')


def send_request(head):
    '''Sents out a request containing the first 5 characters of the hash from
    a password to "Have I Been Pwned?". The results are compared against the
    rest of the hash for that passwords for any matches found.'''

    url = f'https://api.pwnedpasswords.com/range/{head}'
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f'Error in request: {str(res.status_code)}')

    return response.text


def check_hash(hash_list, tail):
    '''Receives a list of potential hashes found on online data breaches, and
    compares them with the tail of a hash for a particular password provided.
    If a match is found here, your password has been compromised! Otherwise it
    returns False.'''

    hashes = (line.split(':') for line in hash_list.splitlines())
    for hash, count in hashes:
        if hash == tail:
            return count

    return False


def hash_password(password):
    '''Creates a hash of the provided password and splits the resulting string
    at the first 5 characters, and returning both parts of the string'''

    password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    head, tail = password_hash[:5], password_hash[5:]
    return head, tail


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('passwords',
        help='A list of passwords to check',
        nargs='*',
    )
    parser.add_argument('-f', '--file',
        help='Path to an existing CSV file containing the passwords to check',
        nargs=1,
        type=pathlib.Path
    )
    parser.add_argument('-d', '--delete',
        help="If a CSV file is provided, it'll be securely deleted by writing  \
        random bytes repeteadly over the original content of the file, before  \
        deleting the file from disk. Provide a number of rounds (by default 3) \
        to overwrite the file for extra security.",
        nargs='?',
        const=3,
        type=int
    )
    parser.add_argument('-v', '--verbose',
        help='prints additional information to terminal output',
        action='store_true'
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
