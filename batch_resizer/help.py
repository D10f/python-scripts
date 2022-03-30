def print_help():
    print("""
    Process images by converting them to different formats and/or resizing them.
    You may provide one or more images and they'll be processed in parallel
    for extra speed (actual gains depend on the hardware it runs on).

    usage: main.py  input [input ...] [-o OUTPUT] [-p] [-w width] [-h height]
                    [-f {.jpg,.jpeg,.png,.webp} [{.jpg,.jpeg,.png,.webp} ...]]
                    [-v] [--version] [--help]

    positional arguments:
      input                 One or more image files to process

    optional arguments:
      -o [OUTPUT], --output-dir [OUTPUT]
                            Directory where processed images will be saved to
      -p, --create-parents  Recursively creates any missing parent directories
      -w WIDTH, --resize WIDTH
                            Pixel width for the output image (preserves aspect-ratio)
      -h HEIGHT, --resize HEIGHT
                            Pixel height for the output image (preserves aspect-ratio)
      -f {webp,jpeg,jpg,png} [{webp,jpeg,jpg,png} ...], --formats {webp,jpeg,jpg,png} [{webp,jpeg,jpg,png} ...]
                            Convert processed file to the selected image format
      -v, --verbose         Writes additional output to the terminal as the program runs
      --help                Show this help message
      --version             Prints the current version for the script

    """)
