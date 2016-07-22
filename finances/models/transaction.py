from mysite import db
from mysite.user.models import AddUser
from finances.models.category import Category, CategoryRE, Action

import re
import StringIO
from ofxparse import OfxParser

class Record(db.Model, AddUser):
    __tablename__ = 'finance_transaction_records'

    id = db.Column(db.String(128), primary_key=True)
    date = db.Column(db.Date)
    payee = db.Column(db.String(128))
    amount = db.Column(db.Float)


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

    cres = db.session.query(CategoryRE).all()
    db_records = set([r.id for r in db.session.query(Record).all()])

    uncat = db.session.query(Category).filter_by(name='uncategorized').first()
    #cre = CategoryRE(1, '.*')
    #action = Action(1, None, cre, uncat)
    #cres.append(cre)

    records = [
        Record(id=t.id, payee=t.payee, date=t.date, amount=t.amount)
        for t in ofx.account.statement.transactions
        if t.id not in db_records
    ]

    transactions = []
    for record in records:
        matched = False
        for cre in cres:
            if cre.match(record):
                transactions += cre.transactions(record)
                matched = True
                break

        if not matched:
            transactions.append({
                'record': {
                    'id': record.id,
                    'date': record.date.strftime('%Y-%m-%d'),
                    'payee': record.payee,
                },
                'date': record.date.strftime('%Y-%m-%d'),
                'category_id': uncat.id,
                'category': uncat.name,
                'name': record.payee,
                'yearly': '0',
                'amount': str(record.amount),
            })

    return transactions

