import asyncio
from turtle import position
from aiohttp import ClientSession
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import urllib.parse
import glob
import os
import re

base_url = "https://www.globalfirepower.com/countries-listing.php"
details_url = "https://www.globalfirepower.com/country-military-strength-detail.php"


def get_country_ids():
    """From the base url, retrieve the links for every country"""
    r = requests.get(base_url)
    soup = bs(r.content, 'lxml')

    return [urllib.parse.parse_qs(urllib.parse.urlparse(link.get('href')).query)["country_id"][0] for link in
            soup.find_all('a', {'href': re.compile(r'country_id')})]


def get_country_ranking_table():
    """From the base url, retrieve the main information for every country"""
    r = requests.get(base_url)
    soup = bs(r.content, 'lxml')

    ranking_table = []
    countries = soup.find_all('div', ['picTrans recordsetContainer boxShadow'])

    for country in countries:
        rank = re.sub("[^0-9]", "", country.div.span.text)
        name = country.find('div', 'countryName').div.span.get_text(strip=True)
        power_index = country.find('div', 'pwrIndxContainer').span.span.get_text(strip=True)[15:]
        progress = country.find('div', 'arrowContainer').img.get('alt').split()[0].lower()
        href = country.find_parent('a').get('href')

        id = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)["country_id"][0]

        ranking_table.append({
            'rank': rank,
            'name': name,
            'power_index': power_index,
            'progress': progress,
            'id': id
        })

    return ranking_table


def get_country_data(html_content, position):
    country_data = []
    soup = bs(html_content, 'lxml')

    # OVERVIEW
    properties_spans = soup.find_all('span', ['textBold textNormal textShadow'])
    values_divs = soup.find_all('div', 'overviewRankHolder')

    properties = [span.text for span in properties_spans]
    values = [re.sub("[^0-9]", "", div.span.text) for div in values_divs]

    country_properties = {properties[i]: values[i] for i in range(len(properties))}

    blocks = soup.find_all('div', 'contentSpecs')

    # MANPOWER
    manpower = blocks[1]
    manpower_labels = manpower.find_all('span', ['textLarge textYellow textBold textShadow'])
    manpower_labels = [span.text[:-1] if ":" in span.text else span.text for span in manpower_labels]
    manpower_labels = ['Paramilitary Total' if label == 'Paramilitary' else label for label in manpower_labels]
    manpower_labels.remove('Manpower Composition')

    manpower_total_population = [manpower.find('span', ['textLarge textWhite textShadow']).text]
    manpower_other_values = [span.text for span in manpower.find_all('span', ['textWhite textShadow'])]
    manpower_values = manpower_total_population + manpower_other_values
    manpower_values = [int(val.replace(',', '')) for val in manpower_values]

    manpower_stats = {manpower_labels[i]: manpower_values[i] for i in range(len(manpower_labels))}
    country_properties.update(manpower_stats)

    # RANK
    country_properties['rank'] = position + 1

    country_data.append(country_properties)

    return pd.DataFrame.from_dict(country_data)


#
# Async HTTP calls
#
def fetch_async(urls):
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_all(urls))
    loop.run_until_complete(future)


async def fetch_all(urls):
    tasks = []
    async with ClientSession() as session:
        for position, url in enumerate(urls):
            task = asyncio.ensure_future(fetch(url, position, session))
            tasks.append(task)
        _ = await asyncio.gather(*tasks)


async def fetch(url, position, session):
    async with session.get(url) as response:
        r = await response.read()

        get_country_data(r, position).to_csv('output/details/rank_{0}.csv'.format(position + 1), index=False)


ranking = pd.DataFrame.from_dict(get_country_ranking_table())
ranking.to_csv('output/ranking_table.csv', index=False, header=True)

urls = ['{0}?country_id={1}'.format(details_url, id) for id in ranking['id']]

fetch_async(urls)

# Merge all csv files from details folder into one !
files = os.path.join('output/details', '*.csv')
files = glob.glob(files)

country_details = pd.concat(map(pd.read_csv, files), ignore_index=True)
country_details.to_csv('output/details/country_details.csv', index=False)

country_details['rank'] = country_details['rank'].astype('int')
ranking['rank'] = ranking['rank'].astype('int')

main_dataset = ranking.merge(country_details, on='rank')

main_dataset.to_csv('output/countries.csv', index=False, sep=';')
print('Done')
