from mysite import db

import datetime
import time
import os
import logging

from selenium.webdriver.common.by import By
import selenium.common.exceptions

logger = logging.getLogger(__name__)

class VanguardFund(db.Model):
    __tablename__ = 'vanguard_funds'

    id = db.Column(db.Integer, primary_key=True)
    fund_type = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    ticker = db.Column(db.String(64), nullable=False)
    asset_class = db.Column(db.String(64), nullable=False)
    exp_ratio = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    minimum = db.Column(db.Integer, nullable=False)

    prices = db.relationship('VanguardPrice', backref='fund')
    dividends = db.relationship('VanguardDividend', backref='fund')
    fees = db.relationship('VanguardFee', backref='fund')

    def __init__(self, id, fund_type, name, ticker, asset_class, exp_ratio):
        self.id = id
        self.fund_type = fund_type
        self.name = name
        self.ticker = ticker
        self.asset_class = asset_class
        self.exp_ratio = exp_ratio

    def __repr__(self):
        return "<VanguardFund(%d, '%s', '%s')>" % ((self.id or 0), self.name, self.ticker)

    @property
    def overview_url(self):
        return "https://personal.vanguard.com/us/funds/snapshot?FundIntExt=INT&FundId=%04d#tab=0" % self.id

    def parse_overview(self, driver):
        logger.info('parse_overview: %s' % self.overview_url)

        table = _web_lookup(self.overview_url, driver, "//table[@id='fundFactsTable']/tbody")[0]

        trs = [
            x for x in table.find_elements(By.TAG_NAME, 'tr')
            if len(x.find_elements(By.TAG_NAME, 'td')) > 1
        ]

        self.category = trs[1].find_elements(By.TAG_NAME, 'td')[1].text
        minimum = trs[3].find_elements(By.TAG_NAME, 'td')[1].text.lower()
        self.minimum = minimum if minimum == 'closed' else _to_float(minimum)

    @property
    def market_data_url(self):
        return "https://advisors.vanguard.com/VGApp/iip/site/advisor/investments/price?fundId=%04d" % self.id

    def parse_market_data(self, driver):
        logger.info('parse_market_data: %s' % self.market_data_url)

        prices_table, dividends_table = _web_lookup(
            self.market_data_url, 
            driver, 
            '//table[@id="priceForm:historicalPricesTable"]',
            '//table[@id="priceForm:priceDistributionsTable"]',
        )

        trs = prices_table.find_elements_by_xpath('tbody/tr')
        for tr in trs[1:]:
            self.add_price([x.text for x in tr.find_elements_by_xpath('td')])

        trs = dividends_table.find_elements(By.TAG_NAME, 'tr')
        for tr in trs[1:]:
            self.add_dividend([x.text for x in tr.find_elements(By.TAG_NAME, 'td')])

    def add_dividend(self, data):
        try:
            dividend_type = data[0]
            price_per_share = _to_float(data[1])
            payable_date = datetime.datetime.strptime(data[2], "%m/%d/%Y").date()
            record_date = datetime.datetime.strptime(data[3], "%m/%d/%Y").date()
            reinvest_date = datetime.datetime.strptime(data[4], "%m/%d/%Y").date()
            reinvest_price = _to_float(data[5])

            fd = [
                fd for fd in self.dividends
                if fd.payable_date == payable_date and fd.dividend_type == dividend_type
            ]

            if fd:
                fd = fd[0]
                fd.price_per_share = price_per_share
                fd.record_date = record_date
                fd.reinvest_date = reinvest_date
                fd.reinvest_price = reinvest_price

            else:
                fd = VanguardDividend(
                    self, dividend_type, price_per_share, payable_date, record_date, 
                    reinvest_date, reinvest_price
                )

            logger.debug(fd)
            db.session.add(fd)

        except (ValueError, IndexError):
            pass

    def add_price(self, data):
        try:
            date = datetime.datetime.strptime(data[0], "%m/%d/%Y").date()
            price = _to_float(data[1])


            fp = [fp for fp in self.prices if fp.date == date]
            if fp:
                fp = fp[0]
                fp.price = price
            else:
                fp = VanguardPrice(self, date, price)

            logger.debug(fp)
            db.session.add(fp)

        except (ValueError, IndexError):
            pass

    def historical_prices(self, driver, directory):
        logger.info('historical prices: %s' % self.market_data_url)

        header, button = _web_lookup(
            self.market_data_url, 
            driver, 
            "//*[@id='fundHeader']/h1",
            "//*[@id='priceForm:sinceInceptionLink']"
        )
        button.click()
        # sometimes file isn't saved in time for os.listdir()
        time.sleep(.5)

        _process_file(directory, header, self.add_price)

    def historical_dividends(self, driver, directory):
        logger.info('historical dividends: %s' % self.market_data_url)

        header, startdate, enddate, button = _web_lookup(
            self.market_data_url, 
            driver, 
            "//*[@id='fundHeader']/h1",
            "//*[@id='priceForm:distPricesStartDate']",
            "//*[@id='priceForm:distPricesEndDate']",
            "//*[@id='priceForm:exportDistributions']",
        )

        mm, dd, yyyy = [int(x) for x in enddate.get_attribute('value').split('/')]
        startdate.send_keys("%d/%d/%d", mm, dd, yyyy-10)

        button.click()
        # sometimes file isn't saved in time for os.listdir()
        time.sleep(.5)
        
        _process_file(directory, header, self.add_dividend)

def _process_file(directory, header, cb):
    name = header.get_attribute('innerHTML').split('&nbsp;')[0]
    files = os.listdir(directory)
    for filename in files:
        with open("%s/%s" % (directory, filename), 'r') as fh:
            lines = fh.read().splitlines()
            if len(lines) > 0 and name in lines[0]:
                for line in lines[2:-1]:
                    cb(line.split(','))

        os.unlink("%s/%s" % (directory, filename))

def _to_float(x):
    return float(x[1:].replace(',', ''))

def _web_lookup(url, driver, *items):
    for attempt in range(1, 4):
        try:
            if attempt > 1:
                logger.info("download attempt %d" % attempt)

            driver.get(url)
            return [driver.find_element_by_xpath(x) for x in items]

        except selenium.common.exceptions.NoSuchElementException as e:
            logger.warn("error downloading page.")
            if attempt < 3:
                time.sleep(3)
            else:
                raise e


class VanguardPrice(db.Model):
    __tablename__ = "vanguard_prices"

    id = db.Column(db.Integer, primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('vanguard_funds.id'))
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('fund_id', 'date', name='_unq_fund_price'),
    )

    def __init__(self, fund, date, price):
        self.fund = fund
        self.date = date
        self.price = price

    def __repr__(self):
        return "<VanguardPrice(%d, '%s', '%s', %f)>" % (
            (self.id or 0), self.fund.ticker, self.date, self.price
        )

class VanguardDividend(db.Model):
    __tablename__ = "vanguard_dividends"

    id = db.Column(db.Integer, primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('vanguard_funds.id'))
    dividend_type = db.Column(db.String, nullable=False)
    price_per_share = db.Column(db.Float, nullable=False)
    payable_date = db.Column(db.Date, nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    reinvest_date = db.Column(db.Date, nullable=False)
    reinvest_price = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('fund_id', 'dividend_type', 'payable_date', 
            name='_unq_fund_dividend'
        ),
    )

    def __init__(
        self, fund, dividend_type, price_per_share, payable_date, record_date, 
        reinvest_date, reinvest_price
    ):

        self.fund = fund
        self.dividend_type = dividend_type
        self.price_per_share = price_per_share
        self.payable_date = payable_date
        self.record_date = record_date
        self.reinvest_date = reinvest_date
        self.reinvest_price = reinvest_price

    def __repr__(self):
        return "<VanguardDividend(%d, '%s', '%s', %f)>" % (
            (self.id or 0), self.fund.ticker, self.payable_date, self.price_per_share
        )

class VanguardFee(db.Model):
    __tablename__ = "vanguard_fees"

    id = db.Column(db.Integer, primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('vanguard_funds.id'))
    fee_type = db.Column(db.String, nullable=False)
    fee = db.Column(db.Float, nullable=False)

    def __init__(self, fund, fee_type, fee):
        self.fund = fund
        self.fee_type = fee_type
        self.fee = fee


