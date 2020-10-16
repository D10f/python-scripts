#!/usr/bin/python3

"""
Process all images inside a directory: resize them, convert to different formats,
remove metadata, add watermarks and compress it all nicely for upload or share
online.

USAGE: resizer.py INPUT_FOLDER [OPTIONS]

TODO: Option to convert to multiple image formats and add support for more formats.
TODO: Option to provide an image to add as a watermark for each image
TODO: Option to preserve original metadata into the processed image
TODO: Option to generate each output image's name using image recognition
"""

from PIL import Image
from itertools import repeat
from pathlib import Path
import concurrent.futures
import argparse
import zipfile
import tarfile
import hashlib
import shutil
import sys
import os
import re
import logging

def main(args):

    args = parse_arguments()
    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)

    # What files will be processed
    valid_files = re.compile(r'.*\.(jpg|jpeg|png|webp)$', re.IGNORECASE)
    images = [file for file in os.listdir(args.input_dir) if valid_files.match(file)]

    # For logging purposes only
    get_images_size = (os.path.getsize(args.input_dir / img) for img in images)
    logging.info(f'{len(images)} images found ({round(sum(get_images_size) / 1000000, 2)} Mb...)')

    # Process each file using multi-processing
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(process_image, images, repeat(args))

    # If an archive flag was passed, make an archive for all the files
    if args.archive:
        make_archive(args)

    # If the delete flag was passed, delete processed files
    if args.delete_original:
        delete_processed(images, args)


def process_image(file, args):

    '''Resizes the image, saves it and if specified it renames it using a hash
    function to randomize its name'''

    logging.info(f'Processing {file}...')

    filename, _ = os.path.splitext(file)
    with Image.open(args.input_dir / file) as img:
        # Get relevant data for the new image
        width = args.dimensions[0] if args.dimensions else img.width
        height = args.dimensions[1] if args.dimensions else img.height
        format = args.format if args.format else img.format

        # Obscure filename with a hashing function
        if args.hash_names:
            logging.info(f'Hashing filename...')
            filename = hashlib.sha1(file.encode('utf-8')).hexdigest()

        # Create new image file with specified dimensions
        img.thumbnail((width, height))
        img.save(f'{args.output_dir / filename}.{format.lower()}', format.upper())


def make_archive(args):

    '''Creates an archive of the specified format to store all processed images.'''

    archive_location = args.output_dir.parent

    # Create archive in tar format
    if args.archive == 'gz':
        with tarfile.open(archive_location / 'processed_images.tar.gz', 'x:gz') as tar:
            tar.add(args.output_dir, arcname='images')

    # Create archive in zip format
    if args.archive == 'ZIP_STORED':
        with zipfile.ZipFile(archive_location / 'processed_images.zip', 'w') as zip:
            os.chdir(args.output_dir)
            for file in os.listdir(args.output_dir):
                zip.write(file)


    # Once archive is created we can delete the output directory
    logging.info(f'Archive created, removing output directory...')
    shutil.rmtree(args.output_dir)


def delete_processed(images, args):

    '''Deletes all files that were processed'''

    logging.info(f'Deleting originals...')
    for img in images:
        os.unlink(args.input_dir / img)


def get_input_directory(path):

    '''Verifies the path provided and returns it as a Path object'''

    p = Path(path)
    if p.exists() and p.is_dir():
        return p.resolve()
    else:
        msg = f'{path} is not a valid directory or does not exist'
        raise argparse.ArgumentTypeError(msg)


def get_output_directory(path):

    '''Verifies the path provided and returns it as a Path object. It'll
    create any necessary directories if they don't exist'''

    p = Path(path) / 'processed_images'
    if p.exists() and p.is_dir():
        return p.resolve()
    elif p.exists() and not p.is_dir():
        msg = f'{path} is not a valid directory'
        raise argparse.ArgumentTypeError(msg)
    else:
        dir = p.resolve()
        os.makedirs(dir)
        return dir


def get_watermark_image(path):

    '''Verifies the path provided and returns an Image object'''

    p = Path(path)
    if p.exists() and p.is_file():
        with Image.open(p.resolve()) as img:
            return img
    else:
        msg = f'{path} is not a valid file or does not exist'
        raise argparse.ArgumentTypeError(msg)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Bulk image processor - resize, convert and organize your images'
    )
    parser.add_argument('input_dir',
        help='Directory location with all images',
        metavar='input_file',
        type=get_input_directory
    )
    parser.add_argument('-o', '--output',
        help='Choose the location for output images (defaults to current directory)',
        dest='output_dir',
        metavar='output_dir',
        type=get_output_directory,
        default=os.getcwd()
    )
    parser.add_argument('-r', '--resize',
        help='Resize images to width and height, preserves aspect-ratio',
        dest='dimensions',
        metavar=('width', 'height'),
        type=int,
        nargs=2
    )
    parser.add_argument('-f', '--format',
        help='Converts image to specified format',
        dest='format',
        choices=['jpg', 'jpeg', 'png', 'webp']
    )
    parser.add_argument('-m', '--metadata',
        help="Preserves the original image's metadata",
        dest='metadata',
        action='store_true'
    )
    parser.add_argument('-u', '--use-hash',
        help='Obscure output filenames using a hashing function',
        dest='hash_names',
        action='store_true'
    )
    parser.add_argument('-d', '--delete',
        help='Deletes original images upon completion',
        dest='delete_original',
        action='store_true'
    )
    parser.add_argument('-w', '--watermark',
        help='Blends the provided image into the processed output',
        dest='watermark',
        metavar='image_file',
        type=get_watermark_image
    )
    parser.add_argument('-v', '--verbose',
        help='Writes output to the terminal as the program runs',
        dest='verbose',
        action='count',
        default=0
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
        action='store_const',
        const='gz'
    )

    return parser.parse_args()

if __name__ == '__main__':
    main()
