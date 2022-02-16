import os
import time
import xattr
import urllib
import urllib.request

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

def blockchain(verbose=0, timeout=10):
    browser = webdriver.Safari()
    browser.set_window_size(1600, 1400)
    browser.implicitly_wait(15)
    for url, destination in (
        ('https://www.blockchain.com/charts/market-cap', 'btc-market-cap.csv'),
        ('https://www.blockchain.com/charts/total-bitcoins', 'btc-total-bitcoins.csv')):
        if verbose:
            print(f'Visiting {url} ...')
        browser.get(url)
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'visx-group')))       
        if verbose:
            print('Graph area loaded')
        try:
            # button = browser.find_element_by_xpath('//button[text()="All Time"]')
            button = browser.find_element(By.XPATH, '//button[text()="All Time"]')
        except selenium.common.exceptions.NoSuchElementException:
            print('Unable to find the "All Time" button')
            return
        try:
            # graph = browser.find_element_by_xpath('//*[name()="linepath" and contains(@d, "M")]')
            graph = browser.find_element(By.XPATH, '//*[name()="path" and contains(@class, "visx-linepath") and contains(@d, "M")]')
        except selenium.common.exceptions.NoSuchElementException:
            print('Unable to find the graph area')
            return
        old = graph.get_attribute('d')
        if verbose:
            print('Clicking the "All Time" button ...')
        button.click()
        k = 0
        for k in range(timeout * 10):
            new = graph.get_attribute('d')
            if new != old:
                break
            if k % 10 == 0:
                print('Waiting for graph data ...')
            time.sleep(0.1)
        select = Select(WebDriverWait(browser, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//*[name()="select"]'))
            ))
        if verbose:
            print('Selecting "CSV Format" ...')
        select.select_by_visible_text('CSV Format')
        filename = os.path.expanduser('~/Downloads/Unknown')
        while not os.path.exists(filename):
            time.sleep(0.1)
        print('File downloaded')
        for a in xattr.listxattr(filename):
            xattr.removexattr(filename, a)
        os.rename(filename, 'blob/{}'.format(destination))

    browser.quit()

#
# https://coinmetrics.io/community-network-data/
#
def coinmetrics(verbose=0):
    url = 'https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv'
    file = 'blob/btc.csv'
    try:
        if verbose:
            print(f'Downloading {file} ...')
        urllib.request.urlretrieve(url, file)
    except:
        print('Download error')
        raise
