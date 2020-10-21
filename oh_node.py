#!/usr/bin/python3

'''
oh_node.py - do you know how much space do all of those node_modules folders
take up in your computer? Neither do I! Let's find out...

Usage: node_way.py ROOT_DIR [-v]

TODO: ignore binary type formats (images, executables, etc)
'''

from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from pathlib import Path
import argparse
import logging
import os
import re

def main():
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(args)

    # total number of files, extenion count and total size (in bytes)
    logging.debug('Counting files...')
    files, types, size = count_files(args.root_dir)

    # count total lines of code
    total_lines = 0

    logging.debug('Counting lines of code...')
    with ThreadPoolExecutor() as executor:
        results = executor.map(count_lines, files, repeat(types))

        # Calculate and format data
        total_lines = sum(result for result in results)
        total_files = len(files)
        total_size = bytes_2_human_readable(size)

        # Calculate the most common file extensions
        high_count = sorted(types.values(), reverse=True)[:10]
        top_10_ext = []
        for k, v in types.items():
            if v in high_count and k != 'none':
                top_10_ext.append((k, v))
            if len(top_10_ext) == 5:
                top_10_ext = sorted(top_10_ext, key=lambda x: x[1], reverse=True)
                break

        logging.debug(f'Found {total_files} total files with {len(types)} different extensions and a total of {total_size}')

        # Print results to terminal output
        print('oh_node.py - Scan Complete')
        print(''.rjust(50, '-'))

        # Total files, and most common extension
        print("Total files".ljust(20, '.') + f"{str(total_files)}".rjust(30, '.'))
        for ext in top_10_ext:
            print(f"  .{ext[0]}".ljust(20) + f"{ext[1]}".rjust(30))

        print('Total size'.ljust(20, '.') + f'{total_size}'.rjust(30, '.'))
        print('Total lines of code'.ljust(20, '.') + f'{str(total_lines)}'.rjust(30, '.'))


def count_lines(file, types):
    '''Counts the lines of code from a text file'''

    lines = 0
    with open(file, 'r') as f:
        try:
            for line in f:
                lines += 1
            return lines
        except UnicodeDecodeError as error:
            # logging.error(f'Error reading {os.path.basename(file)}: {error}')
            return 0


def count_files(root_dir):

    '''
    Counts the number of files and their combined size. It also counts files by
    their extension, including a "None" extension for filenames without it.
    '''

    extension = re.compile(r'.*\.(.*)$')
    total_size = 0
    total_files = []
    total_types = {}

    for current, dirs, files in os.walk(root_dir):

        # ignore files not within a node_modules directory
        if 'node_modules' not in current:
            continue

        for file in files:
            try:
                ext = extension.match(file).group(1)
            except AttributeError:
                ext = 'none'

            # count file extensions, or "none" if filename doesn't have any
            if total_types.get(ext):
                total_types[ext.lower()] += 1
            else:
                total_types[ext.lower()] = 1

            # get absolute path for the file
            file = os.path.join(current, file)

            # add file size to total
            total_size += os.path.getsize(file)

            # add absolute path to total files
            total_files.append(file)

    return (total_files, total_types, total_size)


def bytes_2_human_readable(number_of_bytes):

    '''
    Converts input from bytes and returns in format of Kb, Mb, Gb...
    Credit: https://stackoverflow.com/a/37423778
    '''

    if number_of_bytes < 0:
        raise ValueError("!!! number_of_bytes can't be smaller than 0 !!!")

    step_to_greater_unit = 1024.

    number_of_bytes = float(number_of_bytes)
    unit = 'bytes'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'KB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'MB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'GB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'TB'

    precision = 2
    number_of_bytes = round(number_of_bytes, precision)

    return str(number_of_bytes) + unit


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('root_dir',
        help='root directory to start looking for node_modules.',
        metavar='root_dir'
    )
    parser.add_argument('-v', '--verbose',
        help='prints additional information to terminal output',
        action='store_true'
    )

    return parser.parse_args()


if __name__ == '__main__':
    main()
