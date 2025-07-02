#!/usr/bin/python3

"""
Checks passwords against the "Have I Been Pwned?" (HIBP) database to find out if they've been seen
in any data breaches.
"""

import argparse
import getpass
import hashlib
import io
import pathlib
import subprocess
import sys
import time
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
    account_details: list[tuple[str, str]] = []

    session = requests.Session()
    session.headers.update(
        {"user-agent": __name__, "Add-Padding": str(args.add_padding)}
    )

    if args.keepass_database:
        account_details = parse_kdbx(args.keepass_database, args.keepass_password_file)
    elif args.file:
        account_details = parse_plaintext(args.file, args.skip_hashing)
    else:
        account_details = parse_password_arguments(args.passwords, args.skip_hashing)

    for account, password in account_details:
        head, tail = password[:5], password[5:]
        res = send_request(BASE_URL + head, session, args.request_timeout)

        for hash_tail, count in (line.split(":") for line in res.splitlines()):
            if int(count) > 0 and hash_tail == tail:
                print(f'Found {count} matches for "{account}"')

        time.sleep(args.request_delay)


def parse_password_arguments(
    password_list: list | io.TextIOWrapper, skip_hashing: bool
):
    """
    Parses the positional arguments provided, or from standard input if there aren't any.
    """
    passwords: list[tuple[str, str]] = []

    if isinstance(password_list, io.TextIOWrapper):
        password_list = sys.stdin.readline().strip().split(" ")

    for p in password_list:
        if not skip_hashing:
            p = sha1sum(p)

        passwords.append((p[:5] + "...", p))

    return passwords


def parse_plaintext(filepath: pathlib.Path, skip_hashing: bool):
    """
    Parses a plaintext file where each line is assumed to be its own password. If skip_hashing is
    True, then each line is assumed to be already hashed using SHA-1.
    """
    passwords: list[tuple[str, str]] = []

    with open(filepath, "r", encoding="utf8") as f:
        for line in f.readlines():
            _line = line.strip("\n")

            if not skip_hashing:
                _line = sha1sum(_line)

            passwords.append((line[:5] + "...", _line))

    return passwords


def parse_kdbx(filepath: pathlib.Path, password_file: pathlib.Path | None):
    """
    Parses the Keepass database file to extract the passwords to be checked for data breach against
    the HIPB service.
    """

    if password_file:
        with open(password_file, "r", encoding="utf8") as f:
            keepass_password = f.readline().strip()
    else:
        keepass_password = getpass.getpass(f"Enter password to unlock {filepath}: ")

    keepass_xml = subprocess.run(
        ["keepassxc-cli", "export", "--format", "xml", filepath],
        stdout=subprocess.PIPE,
        input=keepass_password.encode("utf8"),
        check=True,
    )

    passwords: list[tuple[str, str]] = []
    tree = ET.fromstring(keepass_xml.stdout.decode("utf8"))

    for group in tree.findall("Root/Group/Group"):

        if group.find("Name").text == "Recycle Bin":
            continue

        for entry in group.findall("Entry"):
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
                passwords.append((title, sha1sum(password)))

    return passwords


def send_request(url: str, session: requests.Session, timeout: float):
    """
    Sends a request to the HIBP endpoint to check for matches using a range of characters from the
    SHA1 message digest of the password.
    """
    res = session.get(url, timeout=timeout)

    if res.status_code != 200:
        raise RuntimeError(f"Error during request: {res.status_code} - {res.reason}")

    return res.text


def sha1sum(password: str):
    """
    Computes the password using the SHA-1 hashing algorithm and returning a hexadecimal digest.
    """
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def parse_arguments():
    """
    Processes the command line arguments. The positional arguments are strings that can be provided
    inline or read from standard input. In that case, the stream of characters is consumed to create
    the resulting list for the args.passwords argument.
    """

    parser = argparse.ArgumentParser(
        description="""Checks passwords against the "Have I Been Pwned?" (HIBP) database to find out
        if they've been seen in any data breaches."""
    )

    file_input_group = parser.add_mutually_exclusive_group()

    file_input_group.add_argument(
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

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
