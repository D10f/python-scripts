#!/usr/bin/python3

"""
Checks passwords against the "Have I Been Pwned?" (HIBP) database to find out if they've been seen
in any data breaches.
"""


import argparse
import hashlib
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET

import requests

CURRENT_VERSION = "v3.0.0"
REQUEST_TIMEOUT = 9.15
REQUEST_INTERVAL = 1.5
BASE_URL = "https://api.pwnedpasswords.com/range/"


def main():
    """
    The main entrypoint of the script.
    """
    args = parse_arguments()

    if args.keepass_database:
        parse_kdbx(args.keepass_database, args.keepass_password_file)

    # session = requests.Session()
    # session.headers.update(
    #     {"user-agent": __name__, "Add-Padding": str(args.add_padding)}
    # )
    #
    # for password in args.passwords:
    #     hash_head, hash_tail = hash_password(password)
    #     res = send_request(BASE_URL + hash_head, session)
    #     print(res)


def parse_kdbx(filepath: pathlib.Path, password_file: pathlib.Path | None):
    """
    Parses the Keepass database file to extract the passwords to be checked for data breach against
    the HIPB service.
    """

    if password_file:
        with open(password_file, "r", encoding="utf8") as f:
            keepass_password = f.readline().strip()
    else:
        keepass_password = input(f"Enter password to unlock {filepath}: ")

    keepass_xml = subprocess.run(
        ["keepassxc-cli", "export", "--format", "xml", filepath],
        stdout=subprocess.PIPE,
        input=keepass_password.encode("utf8"),
        check=True,
    )

    passwords = []
    tree = ET.fromstring(keepass_xml.stdout.decode("utf8"))

    for root in tree.findall("Root"):
        for group in root.findall("Group"):
            for category in group.findall("Group"):
                for entry in category.findall("Entry"):
                    title = ""
                    password = ""

                    for string in entry.findall("String"):
                        key = string.find("Key")
                        val = string.find("Value")

                        if key.text == "Title":
                            title = val.text
                        if key.text == "Password":
                            password = val.text

                    if title and password:
                        passwords.append((title, password))


def send_request(url: str, session: requests.Session):
    """
    Sends a request to the HIBP endpoint to check for matches using a range of characters from the
    SHA1 message digest of the password.
    """
    res = session.get(url, timeout=REQUEST_TIMEOUT)

    if res.status_code != 200:
        raise RuntimeError(f"Error during request: {res.status_code} - {res.reason}")

    return res.text


def hash_password(password):
    """
    Computes the given password using the SHA1 hashing algorithm, producing a digest in hexadecimal
    format. Returns a tuple of this digest composed of the first five and the remaining characters.
    """
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    head, tail = digest[:5], digest[5:]
    return head, tail


def parse_arguments():
    """
    Processes the command line arguments. The positional arguments are strings that can be provided
    inline or read from standard input. In that case, the stream of characters is consumed to create
    the resulting list for the args.passwords argument.
    """

    parser = argparse.ArgumentParser()

    file_input_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "passwords",
        help="The passwords to check against the HIBP service.",
        nargs="*",
        default=sys.stdin,
    )

    file_input_group.add_argument(
        "-f",
        "--file",
        help="path to text file containing the passwords to check, with one password per line",
        metavar="FILE",
        type=pathlib.Path,
    )

    file_input_group.add_argument(
        "-k",
        "--keepass-database",
        help="""path to a Keepass password database file to read passwords from. The output
        generated will be associated with the title of each entry that was used.""",
        metavar="FILE",
        type=pathlib.Path,
    )

    parser.add_argument(
        "-K",
        "--keepass-password-file",
        help="""path to a file containing the password to unlock the Keepass password database file.
        Use this option for non-interactive usage of this script.""",
        metavar="FILE",
        type=pathlib.Path,
    )

    parser.add_argument(
        "--add-padding",
        help="""padding can be added to ensure all responses contain between 800 and 1000 results
        regardless of the numberof hash suffixes returned by the service. See also:
        https://www.troyhunt.com/enhancing-pwned-passwords-privacy-with-padding""",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--skip-hashing",
        help="""skips hashing the passwords before querying them against the HIBP service. Use this
        when you are sure the input passwords are already hashed. Use with extreme caution!""",
        action="store_true",
    )

    parser.add_argument(
        "-d",
        "--request-delay",
        help="time to wait between requests to the HIBP service, in seconds. Default: 1.5.",
        metavar="SECONDS",
        type=float,
        default=REQUEST_INTERVAL,
    )

    parser.add_argument(
        "-t",
        "--request-timeout",
        help="time to wait for a response from the server, in seconds. Default: 9.15",
        metavar="SECONDS",
        type=float,
        default=REQUEST_TIMEOUT,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="makes the program produce more output as it runs",
        action="count",
        default=0,
    )

    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {CURRENT_VERSION}"
    )

    args = parser.parse_args()

    if not isinstance(args.passwords, list):
        char = ""
        buffer = []
        passwords = []

        while True:
            char = args.passwords.read(1)
            if char == "":
                passwords.append("".join(buffer))
                break
            if char == " ":
                passwords.append("".join(buffer))
                buffer = []
            else:
                buffer.append(char)

        args.passwords = passwords

    return args


if __name__ == "__main__":
    sys.exit(main())
