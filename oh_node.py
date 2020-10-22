#!/usr/bin/python3

'''
oh_node.py - do you know how much space do all of those node_modules folders
take up in your computer? Neither do I! Let's find out...

Usage: node_way.py ROOT_DIR [-v verbose][-t top extensions]

TODO: ignore binary type formats (images, executables, etc)
'''

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

    logging.debug('Counting lines of code...')
    total_lines = count_lines(files)

    # Calculate and format data
    total_files = len(files)
    total_size = bytes_2_human_readable(size)

    logging.debug(f'Found {total_files} total files with {len(types)} different extensions and a total of {total_size}')

    # Print results to terminal output
    print('oh_node.py - Scan Complete')
    print(''.rjust(50, '-'))

    # Total files, and most common extension
    print("Total files".ljust(20, '.') + f"{str(total_files)}".rjust(30, '.'))

    # Optionally pass 0 for --top_ext parameter to skip top extensions
    if args.top_ext:
        for ext in top_extensions(types, top=args.top_ext):
            print(f"  {ext[0]}".ljust(20, '.') + f"{ext[1]}".rjust(30, '.'))

    print('Total size'.ljust(20, '.') + f'{total_size}'.rjust(30, '.'))
    print('Total lines of code'.ljust(20, '.') + f'{str(total_lines)}'.rjust(30, '.'))


def top_extensions(types, top=5):
    '''Counts, sorts and returns the 5 highest items in the types dictionary'''

    # Error checking...
    if top > len(types):
        logging.debug('Showing all extensions...')
        top = len(types)
    if top < 0:
        logging.debug('Showing 5 extensions...')
        top = 5

    print(f"  Showing {top} most common extensions")

    top_ext = []
    high_count = sorted(types.values(), reverse=True)[:top+1]
    for k, v in types.items():
        if v in high_count and k != 'none':
            top_ext.append((k, v))
        if len(top_ext) == top:
            top_ext = sorted(top_ext, key=lambda x: x[1], reverse=True)
            break
    return top_ext


def count_lines(files):
    '''Counts the lines of code from a text file'''

    lines = 0
    for file in files:
        with open(file, 'r') as f:
            try:
                for line in f:
                    lines += 1
            except UnicodeDecodeError as error:
                # TODO: error handling for binary formats
                pass
    return lines


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
    parser.add_argument('-t', '--top-ext',
        help='the number of file extensions to display. Defaults to 5.',
        type=int,
        default=5
    )
    parser.add_argument('-v', '--verbose',
        help='prints additional information to terminal output',
        action='store_true'
    )

    return parser.parse_args()


if __name__ == '__main__':
    main()
