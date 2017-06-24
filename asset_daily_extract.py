import requests
import datetime
import re
import time
import json
import pprint

from mysite import db, create_app
from investments.models.assets import Asset, AssetPrice, AssetDividend

#URL_BASE = 'http://real-chart.finance.yahoo.com/table.csv'
#URL_BASE = 'http://query1.finance.yahoo.com/v7/finance/download'
URL_BASE = 'https://query2.finance.yahoo.com/v8/finance/chart'

def main():
    """
    with requests.Session() as s:
        r = s.get('https://finance.yahoo.com/quote/AAPL/history?p=AAPL')
        lines = r.text.splitlines()

        x = [l for l in lines if re.match('root.App.main =', l)]
        #print x
        j = json.loads(x[0][16:-1])
        #print x[0][16:-1]
        #pprint.pprint(j)

        #eventsData
        #prices
        pprint.pprint(j['context']['dispatcher']['stores']['HistoricalPriceStore']['prices'])
    """

    #url = 'https://query1.finance.yahoo.com/v7/finance/download/AAPL?period1=1492714894&period2=1495306894&interval=1d&events=history&crumb=CCzu7zaIWZm'

    #r2 = requests.get(url, cookies=cookies)
    #print r2.status_code
    #print r2.text
    #return

    #cookies = requests.cookies.cookiejar_from_dict({'B': '6ndb36dc01sqv&b=3&s=28'})
    #cookies = requests.cookies.cookiejar_from_dict({'B': 'e29gjfpcjos7j&b=3&s=ne'})

    #with requests.Session() as s:
    #    x = s.get('https://finance.yahoo.com/quote/AAPL/history?p=AAPL')
    #    m = re.search(r'"CrumbStore":{"crumb":"(.*?)"}', x.content)
    #    print m.group(0)
    #    print m.group(1)

        #print x.content
    #    print x.cookies
    #    print x.headers
    #    print x.links
    #    #print x.json()

    #return
 
    app = create_app()
    with app.app_context():
        end = datetime.date.today() 
        start = end - datetime.timedelta(days=60)
        #start = datetime.date(2016, 4, 1)
        #start = datetime.date(2016, 8, 10)

        #http = urllib3.PoolManager()

        run(start, end)

def run(start, end):
        
    assets = db.session.query(Asset).all()
    for asset in assets[:1]:

        #https://query1.finance.yahoo.com/v7/finance/download/AAPL?period1=1492714894&period2=1495306894&interval=1d&events=history&crumb=CCzu7zaIWZm
        #https://query1.finance.yahoo.com/v7/finance/download/AAPL?period1=1495637830&period2=1498316230&interval=1d&events=history&crumb=ikZfW.SZMeq
        #https://query2.finance.yahoo.com/v8/finance/chart/AAPL?formatted=true&crumb=ikZfW.SZMeq&lang=en-US&region=US&period1=1490331600&period2=1498280400&interval=1d&events=div%7Csplit&corsDomain=finance.yahoo.com
        with requests.Session() as s:
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
    
    #url = '%s?%s' % (URL_BASE, '&'.join(args))
    url = '%s/%s?%s' % (URL_BASE, asset.ticker, '&'.join(args))
    print url
    #r = requests.get(url, cookies=cookies)
    r = s.get(url)
    print r.json()
    continue
    lines = r.text.splitlines()
     
    if [x for x in lines if re.search('404 Not Found', x)]:
        print "Not found: %s: %s - %s" % (asset.ticker, start, end)
        continue
    
    if asset.ticker == 'LMBMX':
        lines.append('2016-05-19,11.43,11.43,11.43,11.43,')
    
    for line in lines[1:]:
        data = line.split(',')
        if re.match(r'\d{4}-\d{1,2}-\d{1,2}$', data[0]):
            date = datetime.date(*map(int, data[0].split('-')))
        else:
            print "Bad line: " + line
            continue
    
        try:
            for i in range(len(data)-1):
                if data[i+1] == '':
                    data[i+1] = '0'
    
            o, h, l, c, v = [None if s=='-' else float(s) for s in data[1:6]]
    
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
    
        except (ValueError, IndexError):
            pass
    
    
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
