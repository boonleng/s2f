import os
import csv
import datetime
import numpy as np
import pandas as pd

import grab

halving_dates = [pd.to_datetime('2009-01-03'),
        pd.to_datetime('2012-11-28'),
        pd.to_datetime('2016-07-09'),
        pd.to_datetime('2020-05-11'),
        pd.to_datetime('2024-03-01')]

def history_from_csv(filename, startrow=0):
    data = []
    header = []
    with open(filename) as file:
        reader = csv.reader(file, delimiter=',')
        for _ in range(startrow):
            next(reader)
        for k, row in enumerate(reader):
            if k > 0:
                data.append(row)
            else:
                header = row
    data = np.array(data)
    return data, header

def str2datetime(x):
    return [datetime.datetime.strptime(n[:10], '%Y-%m-%d') for n in x]

'''
    History of Price, Transaction, and Circulating Coins from CSV Files
    
    - Data points are very sparse, so we will resample them in weeks by default
    - This can be changed to months by using rss = 'M'
'''
def readV1(rss='W-Mon'):
    def valuesFromCSV(key, filename):
        x, _ = history_from_csv(filename)
        d = str2datetime(x[:, 0])
        v = [float(n) for n in x[:, 1]]
        vv = pd.DataFrame({key:v}, index=d)
        return vv
    # wp = valuesFromCSV('Price', 'btc-price.csv').resample(rss).last()
    # wc = valuesFromCSV('Market Cap', 'btc-market-cap.csv').resample(rss).last()
    # wt = valuesFromCSV('Transactions', 'btc-trns.csv').resample(rss).mean()
    # wp = valuesFromCSV('btc-total-bitcoins.csv').resample(rss).last()
    
    wc = valuesFromCSV('Market Cap', 'blob/btc-market-cap.csv').resample(rss).mean()
    # wc = valuesFromCSV('Market Cap', 'blob/btc-market-cap.csv').resample(rss).last()
    
    filename = 'blob/btc-total-bitcoins.csv'
    x, _ = history_from_csv(filename)
    d = str2datetime(x[:, 0])
    s = [float(n) for n in x[:, 1]]
    ss = pd.DataFrame({'Stock':s}, index=d)
    ws = ss.resample(rss).mean().interpolate()
    # ws = ss.resample(rss).last().interpolate()

    z = float(np.mean(np.diff(ws.index)) / 86400e9)
    f = np.concatenate(([s[0], ], np.diff(np.array(s))))
    ff = pd.DataFrame({'Mean Flow':f}, index=d)
    wf = ff.resample(rss).mean().interpolate()        
    wf['Norm Mean Flow'] = wf.values[:, -1] * 365.25
    wf['Tab Flow'] = np.concatenate((ws.values[0], np.diff(ws.values[:, 0])))
    wf['Norm Tab Flow'] = wf.values[:, -1] * 365.25 / z

    # days left in the sampling period
    x = wf.index[-1] - d[-1]
    x = x.total_seconds() / 86400
    # Adjust the last flow to compensate for the remaining days left in the month
    # print(x, z, z / (z - x))
    wf['Norm Tab Flow'].values[-1] *= z / (z - x)

    df = pd.concat([wc, ws, wf], axis=1, join='inner')
    return df

def read(rss='W-Mon'):
    #
    # Data from https://coinmetrics.io/community-network-data/
    #
    filename = 'blob/btc.csv'

    if not os.path.exists(filename):
        grab.coinmetrics()

    values, header = history_from_csv(filename)

    d = str2datetime(values[:, 0])

    k = header.index('CapMrktCurUSD')
    v = [float(n) if len(n) else 0 for n in values[:, k]]
    wc = pd.DataFrame({'Market Cap':v}, index=d).resample(rss).mean()

    k = header.index('SplyCur')
    s = [float(n) if len(n) else 0 for n in values[:, k]]
    ws = pd.DataFrame({'Stock':s}, index=d).resample(rss).last()

    z = float(np.mean(np.diff(ws.index)) / 86400e9)
    f = np.concatenate(([s[0], ], np.diff(np.array(s))))
    ff = pd.DataFrame({'Mean Flow':f}, index=d)
    wf = ff.resample(rss).mean().interpolate()
    wf['Norm Mean Flow'] = wf.values[:, -1] * 365.25
    wf['Tab Flow'] = np.concatenate((ws.values[0], np.diff(ws.values[:, 0])))
    wf['Norm Tab Flow'] = wf.values[:, -1] * 365.25 / z

    # days left in the sampling period
    x = wf.index[-1] - d[-1]
    x = x.total_seconds() / 86400
    # Adjust the last flow to compensate for the remaining days left in the month
    # print(x, z, z / (z - x))
    wf['Norm Tab Flow'].values[-1] *= z / (z - x)

    df = pd.concat([wc, ws, wf], axis=1, join='inner')
    return df
