import requests
import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import urllib.parse
import re

class GlobalFirePowerScraper:

    def get_country_ranking_table():
        """From the base url, retrieve the main information for every country"""

        base_url = "https://www.globalfirepower.com/countries-listing.php"
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
                'rank': int(rank),
                'name': name,
                'power_index': float(power_index),
                'progress': progress,
                'id': id
            })

        return pd.DataFrame.from_dict(ranking_table)

    def get_countries_details(self, ranking):

        details_url = "https://www.globalfirepower.com/country-military-strength-detail.php"
        urls = ['{0}?country_id={1}'.format(details_url, id) for id in ranking['id']]

        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self._fetch_all(urls, ranking))
        loop.run_until_complete(future)

        return ranking

    def _get_country_data(html_content, position):
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

    async def _fetch_all(self, urls, ranking):
        tasks = []
        async with ClientSession() as session:
            for position, url in enumerate(urls):
                task = asyncio.ensure_future(self._fetch(url, position, ranking, session))
                tasks.append(task)
            _ = await asyncio.gather(*tasks)


    async def _fetch(self, url, position, ranking, session):
        async with session.get(url) as response:
            r = await response.read()

            ranking.merge(self, self._get_country_data(r, position), on='rank')
