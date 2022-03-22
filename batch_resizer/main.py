#!/usr/bin/python3

""""
Resize and transform images into different image file formats.
"""

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import argparse
import logging
import pathlib
import sys
import re

CURRENT_VERSION = '1.0.0'
VALID_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
ALPHA_CHANNEL_UNSUPPORTED = ['.jpg', '.jpeg']
FILE_NOT_FOUND_ERR_CODE = 130

# TODO: Validate files based on mime type rather than file extension
# TODO: Verbosity and console output with logging
# TODO: Implement design patterns (strategy?) for additional options per extension

def main():
    args = parse_arguments()
    print(args.usage)
    return

    if args.verbose:
        pass

    if not args.output.exists():
        create_dir(args.output, parents=args.parents)

    image_files = select_images(args.input)

    if not image_files:
        print('No files found, exiting...')
        sys.exit(FILE_NOT_FOUND_ERR_CODE)

    with ThreadPoolExecutor() as executor:
        for img in image_files:
                executor.submit(
                    process_image,
                    img,
                    formats=args.formats,
                    width=args.width,
                    height=args.height,
                    dest=args.output
                )


def select_images(files):
    '''Selects all the valid image files'''
    return [f for f in files if is_valid_format(f)]


def is_valid_format(file):
    '''Verifies input to be a file, and with a valid extension'''
    return file.is_file() and file.suffix.lower() in VALID_FORMATS


def create_dir(target_dir, parents=False):
    '''
    Creates a directory on input location. Parents option set to True will
    create any missing directories.
    '''

    try:
        target_dir.mkdir(parents=parents)
    except FileNotFoundError:
        print('Could not find missing directories, try running with -p flag.')
        sys.exit(FILE_NOT_FOUND_ERR_CODE)


def get_filepath(filename, output_dir, matches=0):
    '''
    Returns a path-like object of the input filename. Verifies if that filename
    already exists in output directory, and appends a suffix to avoid accidental
    data loss.
    '''
    
    result = pathlib.Path(output_dir, filename)

    if result in output_dir.iterdir():
        name, ext = filename.split('.')

        if matches == 0:
            name += '_copy1'

        filename = name.replace(f'_copy{matches - 1}', f'_copy{matches}') + f'.{ext}'
        result = get_filepath(filename, output_dir, matches=matches+1)

    return result


def process_image(img_path, formats=None, width=None, height=None, dest=None):
    '''Converts the image format and/or resizes, preserving aspect ratio.'''

    output_formats = formats or [img_path.suffix.lower()]

    with Image.open(img_path) as img:
        # determine output dimensions
        w = width or img.width
        h = height or img.height

        # resize image object (preserving aspect-ratio)
        img.thumbnail((w, h))

        # Output one file per format
        for f in output_formats:
            filename = img_path.stem

            # If img was resized, append new dimensions to output filename
            if width or height:
                filename += f'_{img.width}-{img.height}'

            filename += f.lower()

            # avoid overwrite by checking for duplicate filenames
            output_file = get_filepath(filename, dest)

            # Remove alpha channel when converting to formats that don't support it
            if f in ALPHA_CHANNEL_UNSUPPORTED:
                img = img.convert('RGB')

            # save image
            print(output_file)
            img.save(output_file)


def parse_arguments():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('input',
        help='Path to the image file(s) to process',
        nargs='+',
        type=pathlib.Path
    )
    parser.add_argument('-o', '--output-dir',
        help="Directory to save processed images. Create dir it if doesn't exist.",
        default=pathlib.os.getcwd(),
        type=pathlib.Path,
        dest='output'
    )
    parser.add_argument('-p', '--create-parents',
        help="Creates missing directories for target output",
        action='store_true',
        dest='parents'
    )
    parser.add_argument('-w', '--width',
        help='Pixel width of the output image',
        type=int,
        metavar='width'
    )
    parser.add_argument('-h', '--height',
        help='Pixel height of the output image',
        type=int,
        metavar='height'
    )
    parser.add_argument('-f', '--formats',
        help='Transform images to the specified format(s)',
        nargs='+',
        choices=['.jpg', '.jpeg', '.png', '.webp']
    )
    parser.add_argument('-v', '--verbose',
        help='Produces additional output as the program runs',
        action='count',
        default=0
    )
    parser.add_argument('--version',
        action='version',
        version=f'%(prog)s v{CURRENT_VERSION}'
    )
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
