from mysite import db
from mysite.models.user import AddUser


class Record(db.Model, AddUser):
    __tablename__ = 'finance_transaction_records'

    id = db.Column(db.String(128), primary_key=True)
    date = db.Column(db.Date)
    payee = db.Column(db.String(128))
    amount = db.Column(db.Float)


