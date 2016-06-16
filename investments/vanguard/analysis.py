from mysite import db

from investments.vanguard import models

import pandas
import numpy
import datetime


def rolling_table(ticker):

    fund = db.session.query(models.VanguardFund).filter(
        models.VanguardFund.ticker==ticker
    ).first()

    ts = pandas.Series(
        [x.price for x in fund.prices], 
        index=pandas.to_datetime([x.date for x in fund.prices]),
    )

    x = pandas.concat(
        [
            ts, 
            pandas.rolling_mean(ts, 30), 
            pandas.rolling_mean(ts, 90),
            pandas.rolling_mean(ts, 180)
        ],
        axis=1
    )

    #return [
    #    (d, x[0][d], x[1][d], x[2][d], x[3][d])
    #    for d in x.index
    #]


    return [ [d] + list(row) for d, row in x.iterrows() ]


