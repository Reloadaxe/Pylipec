from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from validator_collection import checkers
import json


def load_config(path):
    with open(path, 'r') as conf_file:
        conf = json.load(conf_file)
    return conf

def init_driver(chrome_path, chromedriver_path):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--normal")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    driver = webdriver.Chrome(executable_path=chromedriver_path,
                              chrome_options=chrome_options)
    return driver

def load_queries(persons):
    queries = []
    persons = persons.split(',')
    for person in persons:
        query = "site:linkedin.com/in"
        for name_part in person.split():
            query += " AND intitle:" + name_part.strip()
        queries.append(query)
    return queries

def get_profile_urls(driver, n_pages=1):
    linkedin_urls = []
    for i in range(n_pages):
        urls = driver.find_elements_by_class_name('iUh30')
        for url in urls:
            urlPath = url.find_element_by_xpath("./../..").get_attribute("href")
            if checkers.is_url(urlPath):
                linkedin_urls.append(urlPath)
        sleep(0.5)
        if i > 1:
            try:
                next_button_url = driver.find_element_by_css_selector(
                    '#pnnext').get_attribute('href')
                driver.get(next_button_url)
            except NoSuchElementException:
                break
    linkedin_urls_no_rep = sorted(
        list(dict.fromkeys([url for url in linkedin_urls])))
    return linkedin_urls_no_rep

def login(driver, user, pwd):
    username = driver.find_element_by_name('session_key')
    sleep(0.5)
    username.send_keys(user)
    sleep(0.5)
    password = driver.find_element_by_name('session_password')
    password.send_keys(pwd)
    sleep(0.5)
    sign_in_button = driver.find_element_by_class_name('sign-in-form__submit-btn')
    sleep(0.5)
    driver.execute_script("arguments[0].click();", sign_in_button)

def scroll_profile_page(driver):
    last_height = driver.execute_script(
        "return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        sleep(3)
        new_height = driver.execute_script(
            "return document.body.scrollHeight")
        if new_height == last_height:
            break
        else:
            last_height = new_height

def get_entity(entity):
    with open("entities/" + entity + ".json", 'r') as conf_file:
        conf = json.load(conf_file)
    return conf