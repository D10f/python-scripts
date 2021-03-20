'''
Small scraper built as a follow-along of EngineerMan's live stream. I decided
to use the rich module to experiment with displaying data to the terminal in a
'nicer' to look at way.
'''

import requests
from bs4 import BeautifulSoup
from rich import box
from rich.table import Table
from rich.console import Console

url = 'https://yardsalesearch.com/garage-sales.html?zip=90210'

# Initialize console method for printing tables
console = Console()

# Initialize the table and headers
table = Table(
    box=box.SIMPLE,
    show_header=True,
    header_style='bold',
)
table.add_column('Address')
table.add_column('City')
table.add_column('State')
table.add_column('Zip Code')
table.add_column('Latitude', style='dim', justify="right")
table.add_column('Longitude', style='dim', justify="right")
table.add_column('Start Date', style='dim', justify="right")
table.add_column('End Date', style='dim', justify="right")

# The status method adds a spinner on the screen while data is being lodaded
with console.status('Fetching data...'):
    # Fetch the content and store as a 'Soup' object for parsing
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    # Identify in the website the content we're interested in and target it
    for element in soup.find_all('div', { 'class': 'event row featured' }):
        table.add_row(
            element.find('span', { 'itemprop': 'streetAddress' }).text,
            element.find('span', { 'itemprop': 'addressLocality' }).text,
            element.find_all('span', { 'itemprop': 'addressRegion' })[0].text,
            element.find_all('span', { 'itemprop': 'addressRegion' })[1].text,
            element.find('meta', { 'itemprop': 'latitude' })['content'],
            element.find('meta', { 'itemprop': 'longitude' })['content'],
            element.find('meta', { 'itemprop': 'startDate' })['content'],
            element.find('meta', { 'itemprop': 'endDate' })['content']
        )


console.print(table)
