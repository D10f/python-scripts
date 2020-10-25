#!/usr/bin/python3

'''
nama_nama.py - Organize collections of files by changing their names uniformly.
Turn all letters uppercase, lowercase or title-case (first letter of every word
uppercase). Add prefixes and sufixes for files, replace characters with your
chosen delimiters, etc.

USAGE: nama_nama.py DIRECTORY   [title|upper|lower]
                                [separate] [split-at]
                                [prefix] [sufix]

Rename files in a directory uniformly, choose the pattern between all
uppercase, all lowercase or title-case (only first letter of every word
uppercase). Set a delimiter between words i.e.: like-this, like_that or
maybe.this (defaults to space). Set prefix or suffix, ideal for music albums
or photo collections e.g.: Iceland-{filename}

positional arguments:
  input_dir             The target directory where files should be renamed

optional arguments:
  -h, --help            show this help message and exit
  -t, --title           Turns the first letter in every word uppercase
  -u, --upper           Turns every letter uppercase
  -l, --lower           Turns every letter lowercase
  --prefix PREFIX       Adds a prefix character string to every output
                        filename
  --sufix SUFIX         Adds a sufix character string to every output filename
  --separate {-,_,.,,, ,!}
                        Choose how the words in the output filename should be
                        separated by. Defaults to a space
  --split               Splits words in filename, use this to get rid of any
                        existing dividers e.g., underscores, that you want to
                        get rid of (they will be replaced by the "--separate"
                        flag which defaults to a space)
  -v, --verbose         Prints additional information to terminal output
  --dry-run             Processes files in memory and prints results to
                        terminal output

TODO: Option to add numerical sequences as prefixes and sufixes
TODO: Option to remove a pattern from a file i.e., dates, timestamps, etc
TODO: Option to run this script recursively
'''

import argparse
import logging
import pathlib
import shutil
import sys
import os
import re

def main():
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(f'Arguments: {args}')

    if args.case_spec is None:
        logging.debug(f'Naming convention missing')
        print('You must specify a naming convention e.g., tittle case\nExiting...')
        sys.exit()

    # Get all files excluding directories
    logging.debug('Getting files...')
    files = get_files(args.input_dir)

    # Rename files
    logging.debug('Processing...')
    renamed_files = rename_files(files, args)

    # If dry run print results from memory and exit program
    if args.dry_run:
        logging.debug('Entering dry-run mode...')
        for original, renamed in renamed_files:
            print(f'[DR] Renaming: {original} -> {renamed}')
        sys.exit()

    # Write changes to disk
    logging.debug('Writing changes...')
    write_files_to_disk(renamed_files, args)

    logging.debug('End of program')


def write_files_to_disk(files, args):
    '''Renames the files list at the input directory specified'''

    for original, renamed in files:
        # Convert to their absolute path to avoid conflicting issues
        o = os.path.join(args.input_dir, original)
        r = os.path.join(args.input_dir, renamed)
        shutil.move(o, r)


def rename_files(files, args):
    '''Renames the files using the case convention provided. Returns a generator
    expression that yields a tuple with the original and modified filenames'''

    # The following are regular expressions that are created when this function
    # is first called. This avoids unnecessarily creating them on every file
    # iteration, when they are actually used (a few lines below)

    # Split any dividers before joining the word string
    if args.split:
        split_at = re.compile(r'[+=\-_.,;:<>()\[\]\s]')

    # Remove any characters specified
    if args.remove:
        remove_chars = re.compile(f'{args.remove}')

    for file in files:
        filename, ext = os.path.splitext(file)

        # Replace any split characters with separators
        if args.split:
            logging.debug('Replacing split regex...')
            filename = split_at.sub(args.separate, filename)

        # Removes any characters matching the provided string
        if args.remove:
            logging.debug(f'Removing {args.remove} from filename')
            filename = remove_chars.sub('', filename)

        logging.debug(f'Processing: {filename}')
        filename = filename.split(args.separate)

        renamed = []
        for word in filename:
            # What casing to apply
            if args.case_spec == 'title':
                word = word.title()
            if args.case_spec == 'upper':
                word = word.upper()
            if args.case_spec == 'lower':
                word = word.lower()

            renamed.append(word)

        # Apply prefix and sufixes, if any
        if args.prefix:
            renamed.insert(0, args.prefix)
        if args.sufix:
            renamed.append(args.sufix)

        renamed_file = args.separate.join(renamed) + ext

        yield (file, renamed_file)


def get_files(dir):
    '''Matches all files in the provided directory and yields them'''

    for file in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, file)):
            yield file


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='''Rename files in a directory uniformly, choose the pattern
        between all uppercase, all lowercase or title-case (only first letter of
        every word uppercase). Set a delimiter between words i.e.: like-this,
        like_that or maybe.this (defaults to space). Set prefix or suffix, ideal
        for music albums or photo collections e.g.: Iceland-{filename}''',

        usage='''nama_nama.py DIRECTORY [title|upper|lower]
                            [separate] [split-at]
                            [prefix] [sufix]'''
    )
    option = parser.add_mutually_exclusive_group()

    option.add_argument('-t', '--title',
        help='Turns the first letter in every word uppercase',
        action='store_const',
        const='title',
        dest='case_spec'
    )
    option.add_argument('-u', '--upper',
        help='Turns every letter uppercase',
        action='store_const',
        const='upper',
        dest='case_spec'
    )
    option.add_argument('-l', '--lower',
        help='Turns every letter lowercase',
        action='store_const',
        const='lower',
        dest='case_spec'
    )

    parser.add_argument('input_dir',
        help='The target directory where files should be renamed',
        type=pathlib.Path
    )
    parser.add_argument('--prefix',
        help='Adds a prefix character string to every output filename',
    )
    parser.add_argument('--sufix',
        help='Adds a sufix character string to every output filename',
    )
    parser.add_argument('--separate',
        help='''Choose how the words in the output filename should be separated
        by. Defaults to a space''',
        choices=['-', '_', '.', ',', ' ', '!'],
        default=' '
    )
    parser.add_argument('--split',
        help='''Splits words in filename, use this to get rid of any existing
        dividers e.g., underscores, that you want to get rid of (they will be
        replaced by the "--separate" flag which defaults to a space)''',
        action='store_true'
    )
    parser.add_argument('-r', '--remove',
        help='''Removes the matching characters if found on the filename. Use
        with care as changes are non-reversible, is recommended to run with the
        --dry-run flag enabled to see what the expected output would look like.'''
    )
    parser.add_argument('-v', '--verbose',
        help='Prints additional information to terminal output',
        action='store_true'
    )
    parser.add_argument('--dry-run',
        help='Processes files in memory and prints results to terminal output',
        action='store_true'
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
