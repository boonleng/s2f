#!/usr/bin/env python

__version__ = '1.1.0'

'''
imgen.py
s2f

Image Generator

Boonleng

@author: Boonleng Cheong

  Updates:

  1.1     - 2/16/2022
          - Added -c/--calendar option
          - Adjusted locations of halving labels
          - Updated how months after halving is computed

  1.0.3   - 2/14/2022
          - Fixed depecrated API of pandas since 1.4.0

  1.0.2   - 11/27/2021
          - Added option --end-date for a custom end date

  1.0.1   - 4/27/2021
          - Bug fixes and cosmetics

  1.0     - 1/1/2021
          - Started
'''

import os
import sys

__min_python__ = (3, 8, 4)
if sys.version_info < __min_python__:
    version_str = '.'.join(str(k) for k in __min_python__)
    sys.exit(f'Python {version_str} or later is required.\n')

import argparse
import textwrap

df_raw = None

###

def imgen(args):
    import time

    import numpy as np
    import pandas as pd
    import matplotlib
    import matplotlib.pyplot
    import matplotlib.patheffects

    from sklearn.linear_model import LinearRegression, RANSACRegressor

    import data
    import style

    np.set_printoptions(precision=1)

    style.use_dark_theme()

    def v2str(v):
        d = int(np.maximum(-np.log10(v), 0))
        return ('{{:,.{:d}f}}'.format(d)).format(v)

    xfmt = matplotlib.ticker.FuncFormatter(lambda x, pos: v2str(x))
    yfmt = matplotlib.ticker.FuncFormatter(lambda y, pos: '$' + v2str(y))

    # years = matplotlib.dates.YearLocator()             # every year
    # months = matplotlib.dates.MonthLocator()           # every month
    # years_fmt = matplotlib.dates.DateFormatter('%Y')

    global df_raw
    if df_raw is None:
        if args.verbose:
            print('Reading CSV data ...')
        df_raw = data.read(rss='M')
        with pd.option_context('display.max_rows', 6):
            print(df_raw)
            print('')

    if args.end_date:
        ee = pd.to_datetime(args.end_date)
        ii = df_raw.index.get_indexer([ee], method='nearest')[0]
        df = df_raw[:ii+1]
    else:
        df = df_raw[:-1]
    if args.verbose:
        timestr = df.index[-1].strftime('%Y%m%d')
        print(f'Data to {args.end_date} -> {timestr} ...')

    d = df.index                       # Date
    s = df['Stock'].values             # Stock
    f = df['Norm Mean Flow'].values    # Normalized Mean Flow
    f2 = df['Norm Tab Flow'].values    # Normalized Flow from table entries (matches better with PlanB's monthly data)
    mc = df['Market Cap'].values       # Market Capitalization (USD)
    s2f = s / f                        # Stock-to-Flow Ratio
    s2f2 = s / f2                      # Stock-to-Flow Ratio from table entries
    hh = [
        0,
        df.index.get_indexer([pd.to_datetime('2012-11-28')], method='backfill')[0],
        df.index.get_indexer([pd.to_datetime('2016-07-09')], method='backfill')[0],
        df.index.get_indexer([pd.to_datetime('2020-05-11')], method='backfill')[0],
        df.index.get_indexer([pd.to_datetime('2024-03-01')], method='backfill')[0],
    ]
    while hh[-1] == -1:
        hh = hh[:-1]
    if args.verbose > 1:
        print(f'hh = {hh}')

    # Start when market cap > 0, up to month 135
    ii = np.sum(mc == 0)
    ix = np.expand_dims(np.log10(s2f2[ii:]), 1)
    iy = np.log10(mc[ii:])

    linreg = LinearRegression().fit(ix, iy)
    # ransac = RANSACRegressor().fit(ix, iy)

    mx = np.expand_dims(np.logspace(-1, 2.5), 1)
    my = 10 ** linreg.predict(np.log10(mx))
    # print('Linear Regression: log10(y) = {:.4f} * log10(S2F) + {:.4f}'.format(linreg.coef_[0], linreg.intercept_))

    # my2 = 10 ** ransac.predict(np.log10(mx))
    # print('RANSAC Regression: log10(y) = {:.4f} * log10(S2F) + {:.4f}'.format(ransac.estimator_.coef_[0], ransac.estimator_.intercept_))

    path_effects = [
        matplotlib.patheffects.Stroke(linewidth=1.5, foreground=(0.0, 0.0, 0.0, 0.6)),
        matplotlib.patheffects.Normal()
    ]

    fig = matplotlib.pyplot.figure()
    ax = matplotlib.pyplot.axes([0.22, 0.12, 0.73, 0.76])
    ax.tick_params(axis='y')
    ax.plot(mx, my, '-.', linewidth=0.5, color='#FF66DD', zorder=-1)
    ax.set_xlim((0.1, 250))
    ax.set_ylim((1e4, 100e12))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid()
    # From PlanB's article published on 4/27/2020
    ax.plot(58.3, 10.08e12, '.', markersize=20, color='#C29E29', label='Gold (SF58.3, 10.08T)')
    ax.plot(33.3, 561e9, '.', markersize=20, color='#999999', label='Silver (SF33.3, 561B)')
    text = ax.text(48, 8e12, 'Gold (SF58.3, 10.08T)', fontsize=8, ha='right')
    text.set_path_effects(path_effects)
    text = ax.text(27, 5e11, 'Silver (SF33.3, 561B)', fontsize=8, ha='right')
    text.set_path_effects(path_effects)
    if args.verbose > 1:
        print(f'len(d) = {len(d)}')
    for i in range(len(hh)):
        b = hh[i]
        e = hh[i + 1] if i < len(hh) - 1 else len(d) + 1
        x = s2f2[b:e]
        y = mc[b:e]
        w = np.array(df.index[b:e] - df.index[b], dtype=float) / 86400e9 / 365 * 12
        if args.verbose > 1:
            print(f'w = {w}')
        label = 'Genesis' if i == 0 else f'Halving {i}'
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
    text = cax.set_title('Months After Halving')
    text.set_path_effects(path_effects)
    for i, p in enumerate(((2.2, 2e6), (11, 2e8), (25, 2.3e9), (51, 4e10))):
        label = 'Genesis' if i == 0 else 'Halving {}'.format(i)
        text = ax.text(p[0], p[1], label, fontsize=8)
        text.set_path_effects(path_effects)
    text = ax.text(s2f2[-1], mc[-1], '  {:,.0f}B'.format(1.0e-9 * mc[-1]), fontsize=5, ha='left', va='baseline')
    text.set_path_effects(path_effects)
    title_text = ax.set_title('Market Value', fontweight='bold', fontsize=16)
    title_text.set_path_effects([
        matplotlib.patheffects.Stroke(linewidth=1, foreground=(0, 0, 0, 0.7)),
        matplotlib.patheffects.Normal()
    ])

    timestr = time.strftime('%Y-%m-%d', time.localtime())
    fig.text(0.988, 0.02, f'Created on {timestr}', fontsize=4, ha='right', va='baseline')

    timestr = df.index[-1].strftime('%Y%m%d')
    folder = os.path.expanduser('~/Downloads/s2f')
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = f'{folder}/s2f-{timestr}.png'
    if args.verbose:
        print(f'Saving{filename} ...')
    fig.savefig(filename, facecolor='k', dpi=320)
    matplotlib.pyplot.close(fig)

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
        PROG -c 1           produces one calendar year of images until the latest end of month
        PROG -e 20211231    generates an image ending 2021/12/31
    '''.replace('PROG', name)
    epilog = textwrap.dedent('''
        Copyleft 2021-2022 Boonleng Cheong
    ''')
    parser = argparse.ArgumentParser(usage=usage, formatter_class=argparse.RawTextHelpFormatter, epilog=epilog)
    parser.add_argument('-c', '--calendar', type=int, default=0, help='produces N calendar year of images')
    parser.add_argument('-d', '--download', action='store_true', default=False, help='downloads new data')
    parser.add_argument('-e', '--end-date', default=None, help='sets the end day')
    parser.add_argument('-t', '--test', action='store_true', default=False, help='runs a test')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increases verbosity')
    parser.add_argument('--version', action='store_true', help='shows version')
    args = parser.parse_args()

    if args.download:
        import grab
        grab.coinmetrics(verbose=args.verbose)

    if args.test:
        test(args)
    elif args.version:
        print(__version__)
    else:
        if args.calendar:
            import datetime
            import calendar
            today = datetime.date.today()
            dd = []
            m = today.month
            y = today.year - args.calendar
            while not (y == today.year and m == today.month):
                _, e = calendar.monthrange(y, m)
                dd.append(f'{y:04d}{m:02d}{e:02d}')
                m += 1
                if (m == 13):
                    y += 1
                    m = 1
            if args.verbose:
                print(dd)
            for d in dd:
                args.end_date = d
                imgen(args)
        else:
            imgen(args)
