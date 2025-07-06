#!/usr/bin/env python3

"""
Checks passwords against the "Have I Been Pwned?" (HIBP) database to find out if they've been seen
in any data breaches.
"""

import argparse
import getpass
import hashlib
import io
import os
import pathlib
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

CURRENT_VERSION = "3.1.0"
USER_AGENT_TOKEN = os.path.basename(__file__).split(".")[0]
MAX_RETRIES = 3
REQUEST_TIMEOUT = 9.5
REQUEST_INTERVAL = 1.5
BASE_URL = "https://api.pwnedpasswords.com/range/"


def main():
    """
    The main entrypoint of the script.
    """
    args = parse_arguments()
    account_details: list[tuple[str, str]] = []

    if args.keepass_database:
        account_details = parse_kdbx(
            args.keepass_database, args.keepass_password_file, args.keepass_key_file
        )
    elif args.file:
        account_details = parse_plaintext(args.file, args.skip_hashing)
    else:
        account_details = read_positional_args(args.passwords, args.skip_hashing)

    with create_session(args.max_retries, args.add_padding, args.user_agent) as session:
        for account, password in account_details:
            have_i_been_pwned(
                account,
                password,
                session,
                args.request_timeout,
            )
            time.sleep(args.request_delay)


def have_i_been_pwned(
    account: str,
    password: str,
    session: requests.Session,
    timeout: float,
):
    """
    Sends the request to the HIBP server and checks the response.
    """
    head, tail = password[:5], password[5:]

    try:
        response = session.get(BASE_URL + head, timeout=timeout)
        response.raise_for_status()

        for hash_tail, count in (
            line.split(":") for line in response.text.splitlines()
        ):
            if int(count) > 0 and hash_tail == tail:
                print(f'Found {count} matches for "{account}"')

    except requests.exceptions.ConnectionError:
        print(
            """Could not connect to the server. Please check your network settings and/or try again later."""
        )


def create_session(max_retries: int, add_padding: bool, user_agent: str):
    """
    Creates and configures a requests.Session instance to be reused throughout the script.
    """

    session = requests.Session()

    session.headers.update(
        {
            "user-agent": user_agent,
            "Add-Padding": str(add_padding),
        }
    )

    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,
        respect_retry_after_header=True,
    )

    session.mount(BASE_URL, HTTPAdapter(max_retries=retry_strategy))

    return session


def read_positional_args(passwords: list[str] | io.TextIOWrapper, skip_hashing: bool):
    """
    Reads passwords to be processed from the positional arguments, or from standard input if there
    are none provided.
    """
    account_details: list[tuple[str, str]] = []
    password_list = passwords

    if isinstance(passwords, io.TextIOWrapper):
        password_list = sys.stdin.readline().strip().split(" ")

    for password in password_list:
        account_details.append(
            (
                password[:5].ljust(8, "."),
                password if skip_hashing else sha1sum(password),
            )
        )

    return account_details


def parse_plaintext(filepath: pathlib.Path, skip_hashing: bool):
    """
    Parses a plaintext file where each line is assumed to be its own password. If skip_hashing is
    True, then each line is assumed to be already hashed using SHA-1.
    """
    passwords: list[tuple[str, str]] = []

    with open(filepath, "r", encoding="utf8") as f:
        for line in f.readlines():
            line = line.strip("\n")
            passwords.append(
                (line[:5].ljust(8, "."), line if skip_hashing else sha1sum(line))
            )

    return passwords


def parse_kdbx(
    database_file: pathlib.Path,
    password_file: pathlib.Path | None,
    database_keyfile: pathlib.Path | None,
):
    """
    Parses the Keepass database file to extract the passwords to be checked for data breach against
    the HIPB service.

    TODO:
        - [X] Adjust command to execute when key file is provided.
        - [ ] Parse XML correctly for any group structure.
        - [ ] Parse Recycle Bin correctly using UUID since it can be renamed.
    """

    keepass_cli_cmd = ["keepassxc-cli", "export", "--format", "xml", database_file]

    if database_keyfile:
        keepass_cli_cmd.extend(["--key-file", str(database_keyfile)])

    if password_file:
        with open(password_file, "r", encoding="utf8") as f:
            keepass_password = f.readline().strip()
    else:
        keepass_password = getpass.getpass(
            f"Enter password to unlock {database_file}: "
        )

    keepass_xml = subprocess.run(
        keepass_cli_cmd,
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
        "--keepass-key-file",
        help="path to a key file for unlocking the database.",
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
        "--user-agent",
        help="""Defines the user agent string (required by the HIBP service). Defaults to the name
        of the script and version.""",
        default=f"{USER_AGENT_TOKEN}/{CURRENT_VERSION}",
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
        "-r",
        "--max-retries",
        help="number of attempts to retry a connection that has timed out. Default: 3",
        type=int,
        default=MAX_RETRIES,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="makes the program produce more output as it runs",
        action="count",
        default=0,
    )

    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s v{CURRENT_VERSION}"
    )

    return parser.parse_args()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("SIGTERM signal detected. Exiting...")
        sys.exit(1)
