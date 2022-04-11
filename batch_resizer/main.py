#!/usr/bin/python3

""""
Resize and transform images into different image file formats.
"""

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import argparse
import pathlib
import sys
import re

from logger import Logger
from help import print_help

CURRENT_VERSION = '1.0.0'
VALID_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
ALPHA_CHANNEL_UNSUPPORTED = ['.jpg', '.jpeg']
FILE_NOT_FOUND_ERR_CODE = 130

log = Logger(__name__).logger

# TODO: Validate files based on mime type rather than file extension
# TODO: Implement design patterns (strategy?) for additional options
# TODO: Custom help prompt

def main():
    args = parse_arguments()

    if args.help:
        return print_help()

    if args.verbose:
        log.set_verbosity(args.verbose)

    if not args.output.exists():
        create_dir(args.output, parents=args.parents)

    image_files = select_images(args.input)

    if not image_files:
        log.error('No files found, exiting...')
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
        log.error('Could not find missing directories, try running with -p flag.')
        sys.exit(FILE_NOT_FOUND_ERR_CODE)


def rename_image(img_path, format, output_dir):
    '''
    Returns a path-like object of the input filename. Verifies if that filename
    already exists in output directory, and appends a suffix to avoid accidental
    data loss. Recursive call, handle with care :)
    '''

    filename = pathlib.Path(output_dir, img_path.stem + format.lower())

    if filename in output_dir.iterdir():
        if '_copy' not in filename.stem:
            new_filename = filename.stem + '_copy1'
        else:
            _, copy_num = filename.stem.split('_copy')
            old_version = f'_copy{copy_num}'
            new_version = f'_copy{int(copy_num) + 1}'
            new_filename = filename.stem.replace(old_version, new_version)

        return rename_image(pathlib.Path(new_filename), format, output_dir)

    return filename



def resize_image(img, new_width, new_height):
    '''
    Resizes the image to the dimensions provided, preserving aspect-ratio.
    '''
    w = new_width or img.width
    h = new_height or img.height
    enlarged = w > img.width or h > img.height

    img.thumbnail((w, h))

    if enlarged:
        log.warning(f'New size ({img.width}x{img.height}) is larger than original ({img.size})')
    else:
        log.debug(f'Resized to dimensions: {img.width}x{img.height}')


def process_image(img_path, formats=None, width=None, height=None, dest=None):
    '''Converts the image format and/or resizes, preserving aspect ratio.'''

    output_formats = formats or [img_path.suffix.lower()]

    with Image.open(img_path) as img:

        # If custom dimensions were provided, resize image object
        if width or height:
            resize_image(img, width, height)

        # Output one file per format
        for f in output_formats:

            # If img was resized, append new dimensions to output filename
            if width or height:
                dimensions = f'_{img.width}-{img.height}'
                img_path = pathlib.Path(img_path.stem + dimensions)

            # avoid overwrite by checking for duplicate filenames
            output_file = rename_image(img_path, f, dest)

            # Remove alpha channel when converting to formats that don't support it
            if f in ALPHA_CHANNEL_UNSUPPORTED:
                log.debug(f'Removing alpha channel from {img_path}')
                img = img.convert('RGB')

            # save image
            log.info(f'Saving file as: {output_file.resolve()}')
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
        choices=VALID_FORMATS
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
    parser.add_argument('--help',
        action='store_true',
    )

    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
