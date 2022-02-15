#!/usr/bin/env python

__version__ = '1.0.3'

'''
imgen.py
s2f

Image Generator

Boonleng

@author: Boonleng Cheong

  Updates:

  1.0.3   - 2/14/2022
          - Fixed depecrated API of pandas since 1.4.0

  1.0.2   - 11/27/2021
          - Added option --end-date for a custom end date

  1.0.1   - 4/27/2021
          - Bug fixes and cosmetics

  1.0     - 1/1/2021
          - Started
'''

import sys

__min_python__ = (3, 8, 4)
if sys.version_info < __min_python__:
    version_str = '.'.join(str(k) for k in __min_python__)
    sys.exit('Python {} or later is required.\n'.format(version_str))

import os
import time
import xattr
import argparse
import textwrap

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot
import matplotlib.patheffects

from sklearn.linear_model import LinearRegression, RANSACRegressor

import data
import style


###

def grab(args, timeout=10):
    browser = webdriver.Safari()
    browser.set_window_size(1600, 1400)
    browser.implicitly_wait(15)
    for url, destination in (
        ('https://www.blockchain.com/charts/market-cap', 'btc-market-cap.csv'),
        ('https://www.blockchain.com/charts/total-bitcoins', 'btc-total-bitcoins.csv')):
        if args.verbose:
            print('Visiting {}'.format(url))
        browser.get(url)
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'visx-group')))       
        if args.verbose:
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
        if args.verbose:
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
        if args.verbose:
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


def v2str(v):
    d = int(np.maximum(-np.log10(v), 0))
    return ('{{:,.{:d}f}}'.format(d)).format(v)


def imgen(args):
    style.use_dark_theme()

    xfmt = matplotlib.ticker.FuncFormatter(lambda x, pos: v2str(x))
    yfmt = matplotlib.ticker.FuncFormatter(lambda y, pos: '$' + v2str(y))

    years = matplotlib.dates.YearLocator()             # every year
    months = matplotlib.dates.MonthLocator()           # every month
    years_fmt = matplotlib.dates.DateFormatter('%Y')

    if args.verbose:
        print('Reading CSV data ...')

    df = data.read(rss='M')
    df = df[:-1]
    if args.end_date:
        print(f'Clipping data to {args.end_date} ...')
        ee = pd.to_datetime(args.end_date)
        ii = df.index.get_indexer([ee], method='nearest')[0]
        df = df[:ii+1]
    if args.verbose:
        with pd.option_context('display.max_rows', 6):
            print(df)
            print('')

    d = df.index                       # Date
    s = df['Stock'].values             # Stock
    f = df['Norm Mean Flow'].values    # Normalized Mean Flow
    f2 = df['Norm Tab Flow'].values    # Normalized Flow from table entries (matches better with PlanB's monthly data)
    mc = df['Market Cap'].values       # Market Capitalization (USD)
    s2f = s / f                        # Stock-to-Flow Ratio
    s2f2 = s / f2                      # Stock-to-Flow Ratio from table entries
    hh = [
        0,
        df.index.get_indexer([pd.to_datetime('2012-11-28')], method='nearest')[0],
        df.index.get_indexer([pd.to_datetime('2016-07-09')], method='nearest')[0],
        df.index.get_indexer([pd.to_datetime('2020-05-11')], method='nearest')[0],
    ]

    # Start when market cap > 0, up to month 135
    ii = np.sum(mc == 0)
    # ix = np.expand_dims(np.log10(s2f2[ii:136]), 1)
    # iy = np.log10(mc[ii:136])
    ix = np.expand_dims(np.log10(s2f2[ii:]), 1)
    iy = np.log10(mc[ii:])

    if args.verbose:
        print('Data fitting ...')
    linreg = LinearRegression().fit(ix, iy)
    ransac = RANSACRegressor().fit(ix, iy)

    mx = np.expand_dims(np.logspace(-1, 2.5), 1)
    # my = 10 ** linreg.predict(np.log10(mx))
    # print('Linear Regression: log10(y) = {:.4f} * log10(S2F) + {:.4f}'.format(linreg.coef_[0], linreg.intercept_))

    my2 = 10 ** ransac.predict(np.log10(mx))
    print('RANSAC Regression: log10(y) = {:.4f} * log10(S2F) + {:.4f}'.format(ransac.estimator_.coef_[0], ransac.estimator_.intercept_))

    if args.verbose:
        print('Plotting ...')
    fig = matplotlib.pyplot.figure()
    ax = matplotlib.pyplot.axes([0.22, 0.12, 0.73, 0.76])
    ax.tick_params(axis='y')
    # ax.plot(mx, my, '-.', linewidth=0.5, color='#FFDD66', zorder=-1)
    ax.plot(mx, my2, '-.', linewidth=0.5, color='#FF66DD', zorder=-1)
    ax.set_xlim((0.1, 250))
    ax.set_ylim((1e4, 100e12))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid()
    # From PlanB's article published on 4/27/2020
    ax.plot(58.3, 10.08e12, '.', markersize=20, color='#C29E29', label='Gold (SF58.3, 10.08T)')
    ax.plot(33.3, 561e9, '.', markersize=20, color='#999999', label='Silver (SF33.3, 561B)')
    ax.text(48, 8e12, 'Gold (SF58.3, 10.08T)', fontsize=8, ha='right')
    ax.text(27, 5e11, 'Silver (SF33.3, 561B)', fontsize=8, ha='right')
    for i in range(len(hh)):
        b = hh[i]
        e = len(d) if i == len(hh) - 1 else hh[i + 1]
        x = s2f2[b:e]
        y = mc[b:e]
        w = np.array(df.index[b:e] - df.index[b], dtype=float) / 86400e9 / 365.25 * 12
        label = 'Genesis' if i == 0 else 'Halving {}'.format(i)
        hs = ax.scatter(x, y, c=w, vmin=0, vmax=48, cmap='rainbow_r', s=3, label=label)
    loc = []
    for i in range(3, 15):
        loc.append(10 ** i)
    ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator(loc))
    ax.xaxis.set_major_formatter(xfmt)
    ax.yaxis.set_major_formatter(yfmt)
    ax.set_axisbelow(True)
    ax.set_xlabel('S2F')
    cax = fig.add_axes((0.51, 0.2, 0.4, 0.028))
    fig.colorbar(hs, cax=cax, orientation='horizontal')
    loc = []
    for i in range(0, 49, 6):
        loc.append(i)
    cax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(loc))
    cax.set_title('Months After Halving')
    for i, p in enumerate(((2, 1e6), (10, 1e8), (25, 2e9), (55, 5e10))):
        label = 'Genesis' if i == 0 else 'Halving {}'.format(i)
        ax.text(p[0], p[1], label, fontsize=8)
    ax.text(s2f2[-1], mc[-1], '  {:,.0f}B'.format(1.0e-9 * mc[-1]), fontsize=5, ha='left', va='baseline')
    title_text = ax.set_title('Market Value', fontweight='bold', fontsize=16)
    title_text.set_path_effects([
        matplotlib.patheffects.Stroke(linewidth=1, foreground=(0, 0, 0, 0.7)),
        matplotlib.patheffects.Normal()
    ])

    #timestr = datetime.date.today().strftime('%Y%m%d')
    timestr = df.index[-1].strftime('%Y%m%d')
    folder = os.path.expanduser('~/Downloads/s2f')
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = '{}/s2f-{}.png'.format(folder, timestr)
    if args.verbose:
        print('Saving image to {} ...'.format(filename))
    fig.savefig(filename, facecolor='k', dpi=320)

def show_table(file):
    values, _ = data.history_from_csv(file)
    k = 200
    print(values[k:k+14])

def test(args):

    print('Test')
    file = 'blob/btc-market-cap-20211102.csv'
    show_table(file)

    print('')

    file = 'blob/btc-market-cap.csv'
    show_table(file)

###

if __name__ == "__main__":
    # First things first, parse all the arguments
    name = os.path.basename(sys.argv[0])
    usage = '''
    PROG [options]

    examples:

        PROG -v             runs in verbose mode
        PROG -e 20211231    generates an image ending 2021/12/31
    '''.replace('PROG', '{}'.format(name))
    epilog = textwrap.dedent('''
        Copyleft 2021 Boonleng Cheong
    ''')
    parser = argparse.ArgumentParser(usage=usage, formatter_class=argparse.RawTextHelpFormatter, epilog=epilog)
    parser.add_argument('-e', '--end-date', default=None, help='sets the end day')
    parser.add_argument('-d', '--download', action='store_true', default=False, help='downloads new data')
    parser.add_argument('-t', '--test', action='store_true', default=False, help='runs a test')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increases verbosity')
    args = parser.parse_args()

    if args.test:
        test(args)
    else:
        if args.download:
            grab(args)
        imgen(args)
