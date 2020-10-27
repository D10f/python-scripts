#!/usr/bin/python3

'''scanner.py - A simple port scanner to check which ports are open in your local network

USAGE: scanner.py [-h] [-p start end] [-v] hostname

positional arguments:
  hostname              target host to scan for open ports

optional arguments:
  -h, --help            show this help message and exit
  -p start end, --ports start end
                        range of ports to scan for target host
  -v, --verbose         prints additional information to terminal output

TODO: Option to specify specific ports or range
'''

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
import argparse
import logging
import socket
import sys

def main():
	try:
		args = parse_arguments()

		if args.verbose:
			logging.basicConfig(level=logging.INFO)
			logging.debug(args)

			print('-' * 50)
			print(f'Scanning host: {args.hostname}')
			print(f'Scan started: {datetime.now()}')
			print('-' * 50)

			with ThreadPoolExecutor() as executor:
				executor.map(scan_ports, range(int(args.ports[0]), int(args.ports[1])), repeat(args.hostname))

	except KeyboardInterrupt:
		print(f'\nExiting script...')
		sys.exit()
	except socket.gaierror:
		print('Hostname could not be resolved')
		sys.exit()
	except socket.error:
		print('Could not connect to server')
		sys.exit()


def scan_ports(port, hostname):
	'''
	Scans the specified port in the target host
	'''
	# Automatically assigns a port for a TCP connection
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		# Wait 1 second max for connection to remote host
		socket.setdefaulttimeout(1)
		result = s.connect_ex((hostname, port))

		# Report port number only on successful connection
		if result == 0:
			print(f'Port {port} is open!')


def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('hostname',
		help='target host to scan for open ports',
		type=socket.gethostbyname
	)
	parser.add_argument('-p', '--ports',
		help='range of ports to scan for target host',
		metavar=('start', 'end'),
		nargs=2,
		default=(1, 65536)
	)
	parser.add_argument('-v', '--verbose',
		help='prints additional information to terminal output',
		action='store_true'
	)
	return parser.parse_args()


if __name__ == '__main__':
	main()
