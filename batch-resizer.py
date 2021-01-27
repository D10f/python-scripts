#!/usr/bin/python3

"""
Process images by converting them to different formats, resizing them and store
them as compressed archives for easy upload to your cloud. You may provide one
or more images and they'll be processed in parallel for extra speed.

usage: batch-resizer.py [-h] [-v] [-o [OUTPUT]] [-r WIDTH HEIGHT]
                  [-f {webp,jpeg,jpg,png} [{webp,jpeg,jpg,png} ...]]
                  [-z | -t [ARCHIVE]]
                  input [input ...]

positional arguments:
  input                 A single or multiple image files to process

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Writes output to the terminal as the program runs
  -o [OUTPUT], --output [OUTPUT]
                        Directory where processed images will be saved to
  -r WIDTH HEIGHT, --resize WIDTH HEIGHT
                        Pixel width and height of the output image (preserves
                        aspect-ratio)
  -f {webp,jpeg,jpg,png} [{webp,jpeg,jpg,png} ...], --format {webp,jpeg,jpg,png} [{webp,jpeg,jpg,png} ...]
                        Convert processed file to the selected image format
  -z, --zip-archive     Store processed images as .zip archive (uncompressed)
  -t [ARCHIVE], --tar-archive [ARCHIVE]
                        Store processed images as .tar.gz archive (compressed)

TODO: Option to provide an image to add as a watermark for each image
"""

from PIL import Image
from itertools import repeat
import concurrent.futures
import argparse
import logging
import tarfile
import zipfile
import re
import os

def main():
    args = parse_arguments()

    valid_ext = re.compile(r'.*\.(jpe?g|png|webp)$', re.IGNORECASE)
    images = [file for file in args.input if valid_ext.match(file)]

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        print(f'Found {len(images)} images:')

    # Process each file using multi-processing, returns extensions used
    with concurrent.futures.ProcessPoolExecutor() as executor:
        formats = executor.map(process_image, images, repeat(args))

    # Creates an archive with the output images.
    if args.archive:
        make_archive(args, images, next(formats))


def make_archive(args, input, formats):
    '''Creates an archive of the specified format to store output images.'''

    # Store a list of image filenames without their full path or file format
    images = [os.path.splitext(i)[0].split(os.path.sep)[-1] for i in input]

    # Store the file extensions used for this script execution
    formats = set([format.replace('jpg', 'jpeg') for format in formats])

    archive_name = os.path.join(args.output, f'{args.archive}.tar.gz')

    logging.debug(f'Building archive {archive_name}...')

    with tarfile.open(archive_name, 'x:gz') as tar:
        for img in images:
            for ext in formats:
                file_to_add = f'{args.output}{os.path.sep}resized-{img}.{ext}'
                tar.add(file_to_add, arcname=f'resized-{img}.{ext}')

                # Delete the file once is moved into the archive
                os.remove(file_to_add)


def process_image(image, args):
    '''Takes an image file path and process it according to provided arguments'''

    filename, ext = os.path.splitext(os.path.basename(image))
    formats = args.format if args.format else [ext.replace('.', '')]

    # Append short hash to filename to avoid accidental overwrite
    filename = f'resized-{filename}'

    logging.debug(f'Processing file {filename}')

    with Image.open(image) as img:
        # Find width, height and output file format
        width   = args.dimensions[0] if args.dimensions else img.width
        height  = args.dimensions[1] if args.dimensions else img.height

        # Resize image to specified dimensions
        img.thumbnail((width, height))

        # Save image for each specified format
        for f in formats:
            format = 'JPEG' if f.lower().endswith('jpg') else f.upper()
            filepath = f'{os.path.join(args.output, filename)}.{format.lower()}'
            img.save(filepath, format)

    return formats


def parse_arguments():
    '''Parses the arguments used to call this script'''

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose',
        help='Writes output to the terminal as the program runs',
        action='store_true'
    )
    parser.add_argument('input',
        help='A single or multiple image files to process',
        nargs='+'
    )
    parser.add_argument('-o', '--output',
        help='Directory where processed images will be saved to',
        nargs='?',
        default=os.getcwd()
    )
    parser.add_argument('-r', '--resize',
        help='Pixel width and height of the output image (preserves aspect-ratio)',
        nargs=2,
        type=int,
        metavar=('WIDTH', 'HEIGHT'),
        dest='dimensions'
    )
    parser.add_argument('-f', '--format',
        help='Convert processed file to the selected image format',
        nargs='+',
        action='store',
        choices=['webp', 'jpeg', 'jpg', 'png']
    )
    archive_options = parser.add_mutually_exclusive_group()
    archive_options.add_argument('-z', '--zip-archive',
        help='Store processed images as .zip archive (uncompressed)',
        dest='archive',
        action='store_const',
        const='ZIP_STORED'
    )
    archive_options.add_argument('-t', '--tar-archive',
        help='Store processed images as .tar.gz archive (compressed)',
        dest='archive',
        nargs='?',
        const='output'
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
