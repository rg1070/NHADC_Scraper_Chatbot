import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import time


HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        if text:
            return text
    except:
        pass

    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)
        elems = driver.find_elements(By.TAG_NAME, "p")
        text = ' '.join(elem.text for elem in elems).strip()
        driver.quit()
        return text
    except:
        return ""