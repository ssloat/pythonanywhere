import re
from mysite import db

from mysite.user.models import AddUser
from finances.models.category import Category
from finances.models.record import Record

 
class Pattern(db.Model, AddUser):
    __tablename__ = 'finance_patterns'

    id = db.Column(db.Integer, primary_key=True)
    pattern = db.Column(db.String(64))
    minimum = db.Column(db.Float, nullable=True)
    maximum = db.Column(db.Float, nullable=True)

    actions = db.relationship("Action")

    def __init__(self, user, pattern, minimum=None, maximum=None):
        AddUser.__init__(self, user)

        self.pattern = pattern
        self.minimum = minimum
        self.maximum = maximum

    def __repr__(self):
       return "<Pattern('%s')>" % (self.pattern)

    def match(self, record):
        if not re.search(self.pattern, record.payee, flags=re.IGNORECASE):
            return False

        if self.minimum is not None and record.amount < self.minimum:
            return False

        if self.maximum is not None and record.amount > self.maximum:
            return False

        return True

    def transactions(self, record):
        return [action.transaction(record) for action in self.actions]



class Action(db.Model, AddUser):
    __tablename__ = 'finance_actions'

    id = db.Column(db.Integer, primary_key=True)
    pattern_id = db.Column(db.Integer, db.ForeignKey('finance_patterns.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('finance_categories.id'))
    name = db.Column(db.String(64), nullable=True)
    yearly = db.Column(db.Boolean, default=False)
    fixed = db.Column(db.Float, nullable=True)

    category = db.relationship("Category")

    def __init__(self, user, name, pattern, category, yearly=False, fixed=None):
        AddUser.__init__(self, user)

        self.name = name
        self.yearly = yearly
        self.fixed = fixed

        if isinstance(pattern, int):
            self.pattern_id = pattern
        else:
            self.pattern_id = pattern.id

        if isinstance(category, int):
            self.category_id = category
        else:
            self.category = category

    def transaction(self, record):
        return {
            'record': {
                'id': record.id,
                'date': record.date.strftime('%Y-%m-%d'),
                'payee': record.payee,
                'amount': float(record.amount),
            },
            'date': record.date.strftime('%Y-%m-%d'),
            'category_id': self.category.id,
            'category': self.category.name,
            'name': (self.name or record.payee),
            'yearly': ('1' if self.yearly else '0'),
            'amount': self.fixed or float(record.amount),
        }
 
def patterns(user_id):
    return [
        {
            'id': x.id,
            'pattern': x.pattern,
            'minimum': x.minimum,
            'maximum': x.maximum,
        }
        for x in db.session.query(Pattern).filter(Pattern.user_id==user_id).all()
    ]

def pattern(user_id, pattern_id):
    p = db.session.query(Pattern).filter(
        Pattern.user_id==user_id,
        Pattern.id==pattern_id,
    ).first()

    records = [
        r for r in db.session.query(Record).filter(Record.user_id==user_id)
        if p.match(r)
    ]

    actions = db.session.query(Action).filter(
        Action.user_id==user_id,
        Action.pattern_id==pattern_id,
    )

    return { 'pattern': p, 'records': records, 'actions': actions }

def search(user_id, text):
    return [
        {
            'id': p.id,
            'pattern': p.pattern,
            'minimum': p.minimum,
            'maximum': p.maximum,
        }
        for p in db.session.query(Pattern).filter(Pattern.user_id==user_id)
        if re.search(p.pattern, text, flags=re.IGNORECASE)
    ]


