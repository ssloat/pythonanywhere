from mysite import db
from mysite.user.models import AddUser
from finances.models.category import Category, allChildren
from finances.models.record import Record
from finances.models.pattern import Pattern

import json
import datetime
import StringIO
from collections import defaultdict

from ofxparse import OfxParser
from dateutil.relativedelta import relativedelta


class Transaction(db.Model, AddUser):
    __tablename__ = 'finance_transactions'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.String(128), db.ForeignKey('finance_transaction_records.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('finance_categories.id'))
    date = db.Column(db.Date)
    name = db.Column(db.String(64))
    amount = db.Column(db.Float)
    yearly = db.Column(db.Boolean, default=False)

    record = db.relationship("Record", backref='records')
    category = db.relationship("Category")

    def __init__(self, user, date, name, category, amount, record_id=None, yearly=False):
        AddUser.__init__(self, user)

        self.date = date
        self.name = name
        self.amount = amount
        self.record_id = record_id
        self.yearly = yearly

        if isinstance(category, int):
            self.category_id = category
        else:
            self.category = category


    def __repr__(self):
        return "<Tran('%d, %s, %s, %s, %s, %s')>" % (
           (self.id or 0), self.date, self.name, self.category, self.amount, self.yearly
        )

def parse_ofx(text):
    s = StringIO.StringIO(text)
    ofx = OfxParser.parse(s)

    patterns = db.session.query(Pattern).filter(Pattern.pattern!='.').all()
    patterns.append( 
        db.session.query(Pattern).filter(Pattern.pattern=='.').first() 
    )

    db_records = set([r.id for r in db.session.query(Record).all()])

    records = [
        Record(id=t.id, payee=t.payee, date=t.date, amount=t.amount)
        for t in ofx.account.statement.transactions
        if t.id not in db_records
    ]

    transactions = []
    for record in records:
        matched = False
        for pattern in patterns:
            if pattern.match(record):
                transactions += pattern.transactions(record)
                matched = True
                break

    return transactions

def save_transactions(user_id, transactions):
    records = {}
    for transaction in transactions:
        rec = json.loads(transaction['record'])
        records[rec['id']] = rec

        t = Transaction(
            user=user_id, 
            date=datetime.date(*[int(x) for x in transaction['date'].split('-')]),
            name=transaction['name'],
            category=int(transaction['category_id']),
            amount=float(transaction['amount']),
            yearly=transaction['yearly'],
            record_id=rec['id'],
        )

        db.session.add(t)

    db.session.add_all([
        Record(
            user_id=user_id, 
            id=record['id'],
            date=datetime.date(*[int(x) for x in record['date'].split('-')]),
            payee=record['payee'],
            amount=record['amount'],
        ) 
        for record in records.values()
    ])

    db.session.commit()

def monthly_breakdown(from_date, to_date):
    months = []
    tmpdate = datetime.date(from_date.year, from_date.month, from_date.day)
    while tmpdate <= to_date:
        months.append(datetime.date(tmpdate.year, tmpdate.month, 1))
        tmpdate += relativedelta(months=1)

    cats = db.session.query(Category).all()
    catids = dict([(c.id, c.name) for c in cats])
    keys = [m.strftime('%Y-%m') for m in months]
    ts = db.session.query(Transaction)\
        .filter(Transaction.date>=from_date, Transaction.date<=to_date)

    cat_keys = {} 
    results = {}
    for t in ts:
        if t.category.id not in cat_keys:
            cat_keys[t.category.id] = [t.category.id]
            tmp = t.category.parent
            while tmp.name != 'top':
                cat_keys[t.category.id].append(tmp.id)
                tmp = tmp.parent

            cat_keys[t.category.id].append(tmp.id)

        for cid in cat_keys[t.category.id]:
            results[cid] = results.get(cid) or dict([(k, []) for k in keys + ['yearly']])
            if t.yearly:
                results[cid]['yearly'].append(t.amount) 
            else:
                results[cid][t.date.strftime('%Y-%m')].append(t.amount) 

    table = {'headings': ['category', 'average'] + keys[::-1] + ['yearly', 'total'], 'rows': []}
    top = db.session.query(Category).filter(Category.name=='transactions').first()
    for cat in [top]+allChildren(top):
        cols = [(sum(results.get(cat.id, {k: []}).get(k, []), 0.0), k) for k in keys[::-1] + ['yearly']]
        table['rows'].append({
            'category': {
                'id': cat.id,
                'name': cat.name,
                'parent_id': (None if not cat.parent else cat.parent.id),
            },
            'data': cols[:-1], 
            'yearly': cols[-1][0],
            'total': sum([c[0] for c in cols]),
            'average': (sum([c[0] for c in cols[:-1]]) / (len(cols)-1)),
        })

    return table

def transactions(category_id, from_date=None, to_date=None):
    trans = db.session.query(Transaction).join(Category).filter(
        Category.id.in_(
            [category_id] + [c.id for c in allChildren(category_id)]
        ),
#        Transaction.date>=from_date,
#        Transaction.date<=to_date,
    ).order_by(Transaction.date.desc()).all()

    results = []
    monthly = defaultdict(int)
    for tran in trans:
        results.append({
            'id': tran.id,
            'date': tran.date.strftime('%Y-%m-%d'),
            'name': tran.name,
            'category_id': tran.category_id,
            'amount': tran.amount,
            'yearly': tran.yearly,
        })

        if not tran.yearly:
            monthly[tran.date.strftime('%Y/%m')] += tran.amount

    avg = float(sum(monthly.values())) / len(monthly.values())
    name = db.session.query(Category).filter(Category.id==category_id).first().name

    monthly_data = [ ['Month', name, 'Average'] ]
    for k in reversed(sorted(monthly.keys())):
        monthly_data.append([k, abs(monthly[k]), abs(avg)])

    return {
        'transactions': results, 
        'monthly_data': monthly_data,
    }


def update_transactions(transactions):
    for transaction in transactions:
        t = db.session.query(Transaction).filter(Transaction.id==int(transaction['id'])).first()
        
        t.date = datetime.date(*[int(x) for x in transaction['date'].split('-')])
        t.name = transaction['name']
        t.category_id = int(transaction['category_id'])
        t.yearly = transaction['yearly'].lower() == 'true'

        db.session.add(t)

    db.session.commit()

def add_manual_entry(user_id, entry):
    date = datetime.date(*[int(x) for x in entry['date'].split('-')])
    db.session.add_all([
        Transaction(
            user=user_id, 
            date=date,
            name=entry['name'],
            category=int(entry['debit_id']),
            amount=-1.0*float(entry['amount']),
            yearly=False,
        ),
        Transaction(
            user=user_id, 
            date=date,
            name=entry['name'],
            category=int(entry['credit_id']),
            amount=float(entry['amount']),
            yearly=False,
        ),
    ])

    db.session.commit()

