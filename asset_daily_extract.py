import requests
import datetime
import re
import time
import json
import pprint

from mysite import db, create_app
from investments.models.assets import Asset, AssetPrice, AssetDividend

URL_BASE = 'https://query2.finance.yahoo.com/v8/finance/chart'

def main():
    app = create_app()
    with app.app_context():
        end = datetime.date.today() 
        start = end - datetime.timedelta(days=60)
        #start = datetime.date(2016, 4, 1)
        #start = datetime.date(2016, 8, 10)

        run(start, end)

def run(start, end):
    with requests.Session() as s:
        assets = db.session.query(Asset).all()
        for asset in assets:
            query(s, asset, start, end)

def query(s, asset, start, end):
    x = s.get(
        'https://finance.yahoo.com/quote/{ticker}/history?p={ticker}'.format(
            ticker=asset.ticker
        )
    )
    crumb = re.search(r'"CrumbStore":{"crumb":"(.*?)"}', x.content).group(1)

    args = [
        'formatted=true',
        'lang=en-US',
        'region=US',
        'period1=%d' % time.mktime(start.timetuple()), 
        'period2=%d' % time.mktime(end.timetuple()),
        'interval=1d',
        #'events=history',
        'corsDomain=finance.yahoo.com',
        'crumb='+crumb,
    ]
    
    url = '%s/%s?%s' % (URL_BASE, asset.ticker, '&'.join(args))
    print url
    r = s.get(url)
    timestamps = r.json()['chart']['result'][0]['timestamp']
    #meta = r.json()['chart']['result'][0]['meta']

    quotes = r.json()['chart']['result'][0]['indicators']['quote'][0]
    opens = quotes['open']
    highs = quotes['high']
    lows = quotes['low']
    closes = quotes['close']
    volumes = quotes['volume']

    for ts, o, h, l, c, v in zip(timestamps, opens, highs, lows, closes, volumes):
        if c is None:
            continue

        date = datetime.datetime.fromtimestamp(ts).date()
        #print ts, date, o, h, l, c, v

        ap = [ap for ap in asset.prices if ap.date == date]
        if ap:
            ap = ap[0]
            ap.close = c
            ap.open_ = o
            ap.high = h
            ap.low = l
            ap.volume = v
        else:
            ap = AssetPrice(
                #id='%s-%s' % (asset.ticker, date),
                ticker=asset.ticker, 
                date=date, 
                close=c,
                open_=o,
                high=h,
                low=l,
                volume=v
            )
            
        db.session.add(ap)
 
    #if asset.ticker == 'LMBMX':
    #    lines.append('2016-05-19,11.43,11.43,11.43,11.43,')
    
    
    db.session.commit()
    
    
def dividends():
    """
    args.append('g=v')
    url = '%s?%s' % (URL_BASE, '&'.join(args))
    print url
    lines = urllib.urlopen(url).read().splitlines()
     
    if [x for x in lines if re.search('404 Not Found', x)]:
        print "Not found: %s: %s - %s" % (asset.ticker, start, end)
        continue
    
    for line in lines[1:]:
        data = line.split(',')
        date = datetime.date(*map(int, data[0].split('-')))
        dividend = float(data[1])
        
        try:
            ad = [ad for ad in asset.dividends if ap.date == date]
            if ad:
                ad = ad[0]
                ad.value = dividend
            else:
                ad = AssetDividend(
                    #id='%s-%s' % (asset.ticker, date),
                    ticker=asset.ticker, 
                    date=date, 
                    value=dividend,
                )
            
            db.session.add(ad)
    
        except (ValueError, IndexError):
            pass
    
    
    db.session.commit()
    """

if __name__ == '__main__':
    main()
