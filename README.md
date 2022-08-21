# Tyler Technologies Odyssey scraper and parser

This is a scraper to collect and process public case records from the Tyler Technologies Odyssey court records system. If you are a dev or want to file an Issue, please read [CONTRIBUTING](CONTRIBUTING.md).

## Install

1. Clone this repo and navigate to it.
   - `git clone https://github.com/open-austin/indigent-court-stats`
   - `cd indigent-court-stats`
1. Install [poetry](https://python-poetry.org/docs/#installation) and [pyenv](https://github.com/pyenv/pyenv#installation). Benefits are easier env management and reproducable builds.
1. Install libraries.
   - `poetry install`
1. Alternatively with pip, if you don't want to install poetry.
   - `pip install -r requirements.txt`

## Use

_**--help for parameter details.**_

Output of these commands will go to `./data/COUNTY_NAME`

1. Scrape case HTML data through date range.
   - `poetry run python ./src/scraper -start_date 2021-01-01 -end_date 2021-01-10 -county hays`
     - This will scrape 10 days worth of data.
   - Use "python3" instead of "poetry run python" if you are not using poetry.
1. Parse the case data into JSON files.
   - `poetry run python ./src/parser -county hays`

# Compatibility info and stats

I did a manual scraping test up to returning search results, most dates have 0 results, so I didn't test scraping case data from the search on any of these. All detailed county data in [resources/texas_county_data.csv](resources/texas_county_data.csv). Here is are stats pulled from this data:

12 out of 65 do not work, 81.5% do work. 3 are captcha-blocked, 9 are currently impossible (site down or search disabled). 77.8% of the population should be scrapable without captcha solving on Odyssey sites. 2.9% of population is under captcha on them.

4.2% more records could be scraped on non-Odyssey software. On all sites, 84.9% of records are scrapable with captcha solving.

Parser for post 2017 sites is not complete. Parser for pre-2017 sites works well, but needs a lot more testing.

I've recorded county data in the csv for counties representing 97% of Texans.

Marketshare by % of State population (with 97% of data):

| software                    | share |
| --------------------------- | ----- |
| Odyssey                     | 85.7% |
| no online access            | 4.3%  |
| Local Government Solutions  | 1.8%  |
| Aumentum recorder           | 1%    |
| Netdata                     | 1%    |
| edoctec                     | .9%   |
| iDocket                     | .8%   |
| myClerkbooks.com            | .3%   |
| Henschen & Associates, Inc. | .2%   |
| ICON                        | .2%   |
