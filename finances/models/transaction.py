from mysite import db

class Record(db.Model):
    __tablename__ = 'finance_transaction_records'

    id = db.Column(db.String(128), primary_key=True)
    date = db.Column(db.Date)
    payee = db.Column(db.String(128))

class Transaction(db.Model):
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

    def __init__(self, date, name, category, amount, record_id=None, yearly=False):
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

