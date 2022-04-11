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

usage: password_checker.py [-h] [-r plaintext] [-f FILE] [-d] [-t TIMEOUT]
                           [--skip-hashing] [--delete-rounds rounds]
                           [--add-padding] [-v] [--version]

optional arguments:
  -h, --help            show this help message and exit
  -r plaintext, --raw plaintext
                        An inline password to check.
  -f FILE, --file FILE  Path to file containing the passwords to check. Supports
                        plaintext (each password in a separate line) as well
                        as csv files.
  -d, --delete          If a CSV file is provided, it'll be securely deleted
                        by writing random bytes repeteadly over the original
                        content of the file, before deleting the file from
                        disk. Customize the number of overwrites by passing the
                        --delete-rounds option.
  -t TIMEOUT, --timeout TIMEOUT
                        Specifies a time, in millseconds, to wait between
                        requests made against the HIBP. As per the documentation
                        this is rate limited to 1,5s.
  --skip-hashing        Runs the script skipping the hashing step. Use this
                        option only if the input passwords are already hashed
                        using SHA1.
  --delete-rounds rounds
                        Specifies the number of rounds to pass while overwriting
                        data from the files provided (default is 3).
  --add-padding         Padding can be added to ensure all responses contain
                        between 800 and 1000 results regardless of the numberof
                        hash suffixes returned by the service. Read mode about
                        it from this blog post:
                        https://www.troyhunt.com/enhancing-pwned-passwords-privacy-with-padding
  -v, --verbose         Produce extended output
  --version             show program's version number and exit
'''

# TODO: Tell text files apart using built-in mimetypes Python module

import requests
from time import sleep
import argparse
import logging
import hashlib
import pathlib
import secrets
import sys
import csv
import os

CURRENT_VERSION = 'v2.0.0'
SECURE_DELETE_ROUNDS = 3
HIBP_BASE_URL = 'https://api.pwnedpasswords.com/range/'
HIBP_API_TIMEOUT_IN_MS = 1500

# LOGGER OUTPUT COLORS (256-bit)

GRAY = '\x1b[38;5;240m'
BLUE = '\x1b[38;5;39m'
YELLOW = '\x1b[38;5;220m'
RED = '\x1b[38;5;202m'
ORANGE = '\x1b[38;5;160m'
RESET = '\x1b[0m'

logger = logging.getLogger(__name__)

def main(args):
  if args.file:

    if is_csv_file(args.file):
      logger.info(f'Reading from file {args.file.resolve()}...')
      for title, password in get_rows_from_csv(args.file, 'Title', 'Password'):
        have_i_been_pwned(
          password,
          account=title,
          skip_hash=args.skip_hashing,
          padding=args.add_padding,
          timeout=args.timeout
        )

    if is_text_file(args.file):
      logger.info(f'Reading from file {args.file.resolve()}...')
      for password in read_file(args.file):
        have_i_been_pwned(
          password,
          skip_hash=args.skip_hashing,
          padding=args.add_padding,
          timeout=args.timeout
        )

    if args.delete:
      logger.info(f'Erasing file {args.file.resolve()} ({args.delete_rounds} rounds)...')
      delete_file(args.file, rounds=args.delete_rounds)

  if args.raw_password:
    have_i_been_pwned(
      args.raw_password,
      skip_hash=args.skip_hashing,
      padding=args.add_padding,
      timeout=args.timeout
    )


def file_exists(file):
  '''Verifies if the provided file exists'''
  if not file.exists():
    logger.warning(f'{file.resolve()} does not exist. Skipping...')
    return False

  if not file.is_file():
    logger.warning(f'{file.resolve()} is a not a file. Skipping...')
    return False

  return True


def is_csv_file(file):
  'Verifies the file exists and is of format csv'
  return file_exists(file) and file.suffix.lower() == '.csv'


def is_text_file(file):
  '''Verifies if the provided file exists and is of type plaintext'''
  return file_exists(file) and file.suffix.lower() in ['.md', '.txt']


def read_file(file):
  'Returns all the rows in the file'
  with open(file) as f:
    return [line.strip('\n') for line in f.readlines()]


def get_rows_from_csv(file, *select_columns):
  'Returns the values from the tile matching the specified columns.'

  result = []

  with open(file) as f:
    dict_file = csv.DictReader(f)

    for row in dict_file:
      account_info = [row[key] for key in select_columns]
      result.append(account_info)

  return result


def delete_file(file, rounds = SECURE_DELETE_ROUNDS):
  '''Overwrites the contents of a file with random bytes multiple times and
  deletes the file handle from disk. An attacker examining the disk would
  only be able to recover random gibberish instead of the original content.'''

  file_size = os.path.getsize(file)
  with open(file, 'wb') as f:
    logger.info(f'Deleting file...')
    for r in range(rounds):
      f.write(secrets.token_bytes(file_size))
      f.seek(0)
  os.unlink(file)


def have_i_been_pwned(password, account=None, skip_hash=False, padding=False, timeout=HIBP_API_TIMEOUT_IN_MS):
  'Hits the HIBP api to check if any of the passwords have been compromised.'

  if skip_hash:
    head, tail = password[:5], password[5:]
  else:
    head, tail = hash_password(password)

  if not account:
    account = password[:5]

  sleep(timeout / 1000)

  response = send_request(head, padding)
  match = check_hash(response, tail)

  if (match):
    color_print(f'Found match for "{account}" {match} times!', YELLOW)
  else:
    print(f'{account}... OK')


def send_request(head, padding=False):
  '''Sents out a request containing the first 5 characters of the hash from
  a password to "Have I Been Pwned?". The results are compared against the
  rest of the hash for that passwords for any matches found.'''

  url = f'{HIBP_BASE_URL}{head}'
  headers = {
    'user-agent': __name__
  }

  if padding:
    headers.setdefault('Add-Padding', True)

  response = requests.get(url, headers)

  if response.status_code != 200:
    logger.error(response.reason)
    raise RuntimeError(f'Error in request: {str(response.status_code)}')

  return response.text


def check_hash(hash_list, tail):
  '''Receives a list of potential hashes found on online data breaches, and
  compares them with the tail of a hash for a particular password provided.
  If a match is found here, your password has been compromised! Otherwise it
  returns False.'''

  hashes = (line.split(':') for line in hash_list.splitlines())
  for hash, count in hashes:

    if int(count) > 0 and hash == tail:
      return count

  return False


def hash_password(password):
  '''Creates a hash of the provided password and splits the resulting string
  at the first 5 characters, and returning both parts of the string'''

  password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
  head, tail = password_hash[:5], password_hash[5:]
  return head, tail


def clear_line():
  'Clears the last line output to the terminal'
  print('\033[1A', end='\x1b[2K')


def color_print(msg, color_code):
  'prints a message surrounded by color codes for the terminal'
  print(color_code, end='')
  print(msg)
  print(RESET, end='')


def init_logger(verbosity):
  'Defines the handler and formatter for the logger instance.'

  # Define handler (output to console) based on verbosity provided
  stdout_handler = logging.StreamHandler()
  if verbosity > 1:
    logger.setLevel(logging.INFO)
  elif verbosity > 2:
    logger.setLevel(logging.DEBUG)

  # Define formatter for the handler
  fmt = '%(message)s'

  stdout_handler.setFormatter(CustomFormatter(fmt))
  logger.addHandler(stdout_handler)


def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument('-r', '--raw',
    help='An inline password to check.',
    metavar='plaintext',
    dest='raw_password'
  )
  parser.add_argument('-f', '--file',
    help='''Path to file containing the passwords to check. Supports
    plaintext (each password in a separate line) as well as csv files''',
    type=pathlib.Path
  )
  parser.add_argument('-d', '--delete',
    help='''If a CSV file is provided, it'll be securely deleted by writing
    random bytes repeteadly over the original content of the file, before
    deleting the file from disk. Customize the number of overwrites by
    passing the --delete-rounds option.''',
    action='store_true'
  )
  parser.add_argument('-t', '--timeout',
    help='''Specifies a time, in millseconds, to wait between requests made
    against the HIBP. As per the documentation this is rate limited to 1,5s''',
    type=int,
    nargs=1,
    default=HIBP_API_TIMEOUT_IN_MS
  )
  parser.add_argument('--skip-hashing',
    help='''Runs the script skipping the hashing step. Use this option only
    if the input passwords are already hashed using SHA1.''',
    action='store_true'
  )
  parser.add_argument('--delete-rounds',
    help='''Specifies the number of rounds to pass while overwriting data
    from the files provided (default is 3).''',
    type=int,
    metavar='rounds',
    default=SECURE_DELETE_ROUNDS
  )
  parser.add_argument('--add-padding',
    help='''Padding can be added to ensure all responses contain between 800
    and 1000 results regardless of the numberof hash suffixes returned by
    the service. Read mode about it from this blog post:
    https://www.troyhunt.com/enhancing-pwned-passwords-privacy-with-padding''',
    action='store_true',
  )
  parser.add_argument('-v', '--verbose',
    help='Produce extended output',
    action='count',
    default=0
  )
  parser.add_argument('--version',
    action='version',
    version=f'%(prog)s {CURRENT_VERSION}'
  )

  return parser.parse_args()


class CustomFormatter(logging.Formatter):
  """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

  def __init__(self, fmt):
    super().__init__()
    self.fmt = fmt
    self.FORMATS = {
      logging.DEBUG: GRAY + self.fmt + RESET,
      logging.INFO: BLUE + self.fmt + RESET,
      logging.WARNING: YELLOW + self.fmt + RESET,
      logging.ERROR: RED + self.fmt + RESET,
      logging.CRITICAL: ORANGE + self.fmt + RESET
    }

  def format(self, record):
    log_fmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(log_fmt)
    return formatter.format(record)


if __name__ == '__main__':
  args = parse_arguments()
  init_logger(args.verbose)
  sys.exit(main(args))
