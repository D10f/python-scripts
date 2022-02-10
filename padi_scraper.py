#!/usr/bin/python3

'''
A web scraper that collects all diving shop listed by PADI
'''

from time import sleep
import requests
import json

delay = 10
current_page = 0
total_pages = 118
size = 50
key = '516d8696d377'

diveshops = []
sponsored_diveshops = []

url = ''

def save_files():
    '''Saves JSON data retrieved from the API to disk'''

    with open('diveshops.json', 'w') as diveshop_file:
        json.dump(diveshops, diveshop_file)

    with open('sponsored_diveshops.json', 'w') as sponsored_diveshop_file:
        json.dump(sponsored_diveshops, sponsored_diveshop_file)


def show_progress():
    '''Prints out to the console the current progress of the scraper'''

    processed_pages = current_page + 1
    percentage = processed_pages * 100 / total_pages
    print(f'{processed_pages} pages downloaded ({round(percentage, 2)}%)')


def main():
    '''Runs on a loop until all available endpoints have been consumed'''

    while True:

        # Make the request and parse JSON data
        response = requests.get(url).text
        json_response = json.loads(response)

        # Extract from the response the data we are interested in saving
        diveshop_results = json_response['results']
        sponsored_results = json_response['sponsoredResults']

        # Append to global variables each time since response is paginated
        diveshops.extend(diveshop_results)
        sponsored_diveshops.extend(sponsored_results)

        # Print progress to the console
        show_progress()

        try:
            # Attempt to fetch next page from API. Will error out on the very last one
            url = json_response['_links']['next']['href']

            # Artificially delay next request to avoid spamming the server
            sleep(5)

        except 'next':
            break

    save_files()
    print(f'{len(diveshops)} dive shops found')
    print(f'{len(sponsored_diveshops)} sponsored dive shops found')
    print('DONE!')


main()
