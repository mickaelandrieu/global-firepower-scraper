import cloudscraper
from bs4 import BeautifulSoup as bs
import pandas as pd
import urllib.parse
import re

class GlobalFirePowerScraper:
    def __init__(self):
        self.ranking = pd.DataFrame()
        self.country_details = pd.DataFrame()

    def __get_country_ranking_table(self) -> pd.DataFrame:
        """From the base url, retrieve the main information for every country"""

        base_url = "https://www.globalfirepower.com/countries-listing.php"
        scraper = cloudscraper.create_scraper()
        soup = bs(scraper.get(base_url).text, "lxml")

        ranking_table = []
        countries = soup.find_all("div", ["picTrans recordsetContainer boxShadow"])

        for country in countries:
            rank = re.sub("[^0-9]", "", country.div.span.text)
            name = country.find("div", "countryName").div.span.get_text(strip=True)
            power_index = country.find("div", "pwrIndxContainer").span.span.get_text(
                strip=True
            )[15:]
            progress = (
                country.find("div", "arrowContainer").img.get("alt").split()[0].lower()
            )
            href = country.find_parent("a").get("href")

            id = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)["country_id"][
                0
            ]

            ranking_table.append(
                {
                    "rank": int(rank),
                    "name": name,
                    "power_index": float(power_index),
                    "progress": progress,
                    "id": id,
                }
            )

        self.ranking = pd.DataFrame.from_dict(ranking_table)

        return self.ranking

    def __get_countries_details(self) -> pd.DataFrame:

        details_url = (
            "https://www.globalfirepower.com/country-military-strength-detail.php"
        )
        urls = [
            "{0}?country_id={1}".format(details_url, id) for id in self.ranking["id"]
        ]

        self.__fetch_all(urls)

        return self.country_details

    def get_armies_information(self) -> dict:
        self.ranking = self.__get_country_ranking_table()
        self.country_details = self.__get_countries_details()

        return self.ranking.merge(self.country_details, on="rank").to_dict()

    def __get_country_data(self, html_content, position) -> dict:
        country_data = []
        soup = bs(html_content, "lxml")

        # OVERVIEW
        properties_spans = soup.find_all("span", ["textBold textNormal textShadow"])
        values_divs = soup.find_all("div", "overviewRankHolder")

        properties = [span.text for span in properties_spans]
        values = [re.sub("[^0-9]", "", div.span.text) for div in values_divs]

        country_properties = {properties[i]: values[i] for i in range(len(properties))}

        blocks = soup.find_all("div", "contentSpecs")

        # MANPOWER
        manpower = blocks[1]
        manpower_labels = manpower.find_all(
            "span", ["textLarge textYellow textBold textShadow"]
        )
        manpower_labels = [
            span.text[:-1] if ":" in span.text else span.text
            for span in manpower_labels
        ]
        manpower_labels = [
            "Paramilitary Total" if label == "Paramilitary" else label
            for label in manpower_labels
        ]
        manpower_labels.remove("Manpower Composition")

        manpower_total_population = [
            manpower.find("span", ["textLarge textWhite textShadow"]).text
        ]
        manpower_other_values = [
            span.text for span in manpower.find_all("span", ["textWhite textShadow"])
        ]
        manpower_values = manpower_total_population + manpower_other_values
        manpower_values = [int(val.replace(",", "")) for val in manpower_values]

        manpower_stats = {
            manpower_labels[i]: manpower_values[i] for i in range(len(manpower_labels))
        }
        country_properties.update(manpower_stats)

        # RANK
        country_properties["rank"] = position + 1

        country_data.append(country_properties)

        return pd.DataFrame.from_dict(country_data)

    def __fetch_all(self, urls):
        scraper = cloudscraper.create_scraper()
        for position, url in enumerate(urls):

            html_response = scraper.get(url).text

            country_data = self.__get_country_data(html_response, position)
            if self.country_details.empty:
                self.country_details = country_data
            else:
                self.country_details = pd.concat(
                    [self.country_details, country_data], axis="rows"
                )
