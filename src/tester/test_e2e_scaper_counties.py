import unittest
import scraper


class ScraperCountyTests(unittest.TestCase):

    def test_e2e_scraper_hays(self):
        scraper.Scraper().scrape(
            county="hays",
            start_date="2022-05-10",
            end_date="2022-05-10",
            judicial_officers=["Updegrove, Robert"],
            ms_wait=0,
        )
