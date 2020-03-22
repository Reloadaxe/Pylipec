from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException
from utils import init_driver, get_profile_urls, login,\
    load_config, load_queries
from time import sleep
from classes.UserScraper import UserScraper
import argparse
import sys
import json
import uuid

parser = argparse.ArgumentParser(
    description=("Scrape linkedin profiles based on the " +
                 "queries specified in the conf file")
)
parser.add_argument(
    '-c', '--conf',
    type=str,
    metavar='',
    required=True,
    help='Specify the path of the configuration file'
)
parser.add_argument(
    '-p', '--persons',
    type=str,
    metavar='',
    required=True,
    help='Specify the names of the persons you want to search separated by a comma and delimited by quotes'
)
args = parser.parse_args()
conf = load_config(args.conf)
queries = load_queries(args.persons)
parameters = conf["parameters"]
credentials = conf["credentials"]
CHROME_PATH = parameters["CHROME_PATH"]
CHROMEDRIVER_PATH = parameters["CHROMEDRIVER_PATH"]
N_PAGES = parameters["N_PAGES"]
LINUSERNAME = credentials["LINUSERNAME"]
LINPWD = credentials["LINPWD"]
driver = init_driver(CHROME_PATH, CHROMEDRIVER_PATH)
driver.get("https://www.linkedin.com")
login(driver, LINUSERNAME, LINPWD)
us = UserScraper(driver)
users_data = []
for query in queries:
    driver.get("https://www.google.com")
    sleep(2)
    search_query = driver.find_element_by_name('q')
    try:
        search_query.send_keys(query)
    except ElementNotInteractableException:
        print("ERROR :: Cannot send query. Google might be blocking")
        sys.exit(1)
    sleep(0.5)
    search_query.send_keys(Keys.RETURN)
    profile_urls = get_profile_urls(driver, N_PAGES)
    if len(profile_urls) == 0:
        print()
        print("WARNING :: " +
              "Could not get any URLs for the query\n" + query)
        print("Please double-check that Google is not " +
              "blocking the query")
        continue
    for url in profile_urls:
        users_data.append(us.scrape_user(query, url))
filename = 'data/'+ str(uuid.uuid4()) +'.json'
with open(filename, 'w') as outfile:
    json.dump(users_data, outfile, ensure_ascii=False)
print("Data saved to " + filename)
driver.quit()
