from nose.tools import assert_equals
import datetime
import logging

from mysite import db
from finances.models.transaction import Record
from finances.models.category import Category
from finances.models.pattern import Pattern, Action

from t.base_test import TestBase

class TestPattern(TestBase):

    def setUp(self):
        super(TestPattern, self).setUp()

        def create_category(*args):
            c = Category(self.user, *args)
            db.session.add(c)
            db.session.commit()
            return c

        top = create_category('top', None, 0)
        child = create_category('child', top)
        gchild = create_category('grandchild', child)
        uncat = create_category('uncategorized', top)


        pattern = Pattern(self.user, 'pattern')
        db.session.add(pattern)
        db.session.commit()

        action1 = Action(self.user, 'one', pattern, gchild)
        action2 = Action(self.user, 'two', pattern, gchild, yearly=True)

        db.session.add_all([pattern, action1, action2])


    def test_pattern(self):
        pattern = db.session.query(Pattern).filter(Pattern.pattern=='pattern').first()

        rec = Record(id=1, date=datetime.date(2016, 6, 30), payee='pattern', amount=1.23)

        pattern = db.session.query(Pattern).first()
        assert_equals(pattern.match(rec), True)

        expected = [
            {
                'record': {
                    'id': 1,
                    'date': str(datetime.date(2016, 6, 30)),
                    'payee': 'pattern',
                    'amount': 1.23,
                },
                'date': str(datetime.date(2016, 6, 30)),
                'category_id': 3,
                'category': 'grandchild',
                'name': 'one',
                'yearly': '0',
                'amount': 1.23,
            },
            {
                'record': {
                    'id': 1,
                    'date': str(datetime.date(2016, 6, 30)),
                    'payee': 'pattern',
                    'amount': 1.23,
                },
                'date': str(datetime.date(2016, 6, 30)),
                'category_id': 3,
                'category': 'grandchild',
                'name': 'two',
                'yearly': '1',
                'amount': 1.23,
            },
        ]
    
        assert_equals(pattern.transactions(rec), expected)


