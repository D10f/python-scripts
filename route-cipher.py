#!/usr/bin/env python3

"""
reoute-cipher.py
"""

from pathlib import Path
from copy import deepcopy
from argparse import ArgumentParser
import logging
import sys

# TEST_CIPHERTEXT = '16 12 8 4 0 1 5 9 13 17 18 14 10 6 2 3 7 11 15 19'
# TEST_COLS = 4
# TEST_ROWS = 5
# TEST_KEY = '-1 2 -3 4' # negative reads upwards, positive downwards

logger = None

def main():
  args = parse_arguments()
  logger = init_logger(args.verbose)
  
  if args.file:
    logger.info(f'Reading from file at {args.file.resolve()}')
    with open(args.file) as f:
      ciphertext = f.read()
  else:
    ciphertext = args.message

  validate_length(ciphertext, args.rows, args.columns)

  translation_matrix = create_matrix(
    ciphertext,
    args.key,
    args.columns,
    args.rows
  )

  print(logger.getEffectiveLevel())

  if logger.getEffectiveLevel() >= 10:
    print_matrix(translation_matrix)

  plaintext = decrypt(translation_matrix, args.rows)

  print(plaintext)


def validate_length(ciphertext, rows, cols):
  """
  Checks that the input columns and rows are valid respective to the
  ciphertext length.
  """
  factors = []
  len_cipher = len(ciphertext.split())

  # Exclude 1x1 grids as that would be ciphertext
  for i in range(2, len_cipher):
    if len_cipher % i == 0:
      factors.append(i)
  
  if rows * cols != len_cipher:
    print("Error - Input columns and rows not factors of length of ciphertext.")
    sys.exit(1)


def validate_key(key, cols):
  """Turn key into list of integers and checks it for validity"""

  key_int = [int(k) for k in key.split()]
  lowest = min(key_int)
  highest = max(key_int)

  if 0 in key_int:
    print('Invalid key - 0 is not a valid value')
    sys.exit(1)

  if (
    len(key_int) != cols or \
    lowest < -cols or \
    highest > cols
  ):
    print('Invalid key - Invalid number of of columns and/or rows')

  return key_int


def decrypt(matrix, rows):
  plaintext = ''
  matrix_copy = deepcopy(matrix)
  
  for _ in range(rows):
    for col in matrix_copy:
      word = str(col.pop())
      plaintext += word + ' '

  return plaintext


def create_matrix(ciphertext, key, cols, rows):
  """Turns a given ciphertext into a matrix of size cols x rows"""

  ciphertext_list = ciphertext.split()
  translation_matrix = [None] * cols
  start = 0
  stop  = rows

  for k in validate_key(key, cols):

    col_items = ciphertext_list[start:stop]

    # Reverse order of ciphertext based on sign on key
    if int(k) > 0:
      col_items = list(reversed(col_items))

    # Subtract one for python's 0 index
    translation_matrix[abs(int(k)) - 1] = col_items
    
    # Increase counters for next iteration
    start += rows
    stop += rows

  return translation_matrix


def print_matrix(matrix):
  print('Translation Matrix', *matrix, sep='\n')


def init_logger(verbosity):
  logger = logging.getLogger(__name__)
  if verbosity == 1:
    logger.setLevel(logging.INFO)
  if verbosity > 1:
    logger.setLevel(logging.DEBUG)
  return logger


def parse_arguments():
  parser = ArgumentParser()

  parser.add_argument('-k', '--key',
    help='key used to encrypt/decrypt the message'
  )
  parser.add_argument('-c', '--columns',
    help='Number of "columns" to use to create the route cipher',
    type=int
  )
  parser.add_argument('-r', '--rows',
    help='Number of "rows" to use to create the route cipher',
    type=int
  )

  operations = parser.add_mutually_exclusive_group(required=True)
  operations.add_argument('-e', '--encrypt',
    help='run script with encryption instructions',
    action='store_true'
  )
  operations.add_argument('-d', '--decrypt',
    help='run script with decryption instructions',
    action='store_true'
  )

  source = parser.add_mutually_exclusive_group(required=True)
  source.add_argument('-m', '--message',
    help='string to either encrypt or decrypt'
  )
  source.add_argument('-f', '--file',
    help='path to file containing the ciphertext',
    type=Path
  )

  parser.add_argument('-v', '--verbose',
    help='prints additional information to terminal output',
    action='count'
  )
  return parser.parse_args()


if __name__ == '__main__':
  main()