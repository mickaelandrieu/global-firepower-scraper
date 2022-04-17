import pytest
from globalfirepower.globalfirepower import GlobalFirePowerScraper


class TestGlobalFirePowerScraper:
    def test_scrapping(self, **kwargs):
        gfi_scraper = GlobalFirePowerScraper()

        assert isinstance(
            gfi_scraper.get_armies_information(), dict
        ), "We should get a dictionnary"
