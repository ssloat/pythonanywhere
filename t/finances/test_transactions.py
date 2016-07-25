from nose.tools import assert_equals
import datetime
import logging


from mysite import db
from finances.models.transaction import Transaction
from finances.models.category import Category, create_categories
from finances.models.pattern import Pattern, Action

from t.base_test import TestBase

class TestTransaction(TestBase):

    def setUp(self):
        super(TestTransaction, self).setUp()

        top = Category(self.user, 'top', None, 0)
        child = Category(self.user, 'child', top)
        gchild = Category(self.user, 'grandchild', child)
        uncat = Category(self.user, 'uncategorized', top)

        pattern = Pattern(self.user, 'pattern')
        db.session.add(pattern)
        db.session.commit()

        action1 = Action(self.user, 'one', pattern, gchild)
        action2 = Action(self.user, 'two', pattern, gchild, yearly=True)

        db.session.add_all([top, child, gchild, pattern, action1, action2, uncat])


    def test_category(self):
        child = db.session.query(Category).filter(Category.name=='child').first()

        assert_equals(child.name, 'child')
        assert_equals(child.parent.name, 'top')
        assert_equals(len(child.children), 1)

        pattern = db.session.query(Pattern).first()
        """
        for action, id in zip(pattern.actions, ('a', 'b')):
            action.load(id, datetime.date(2016, 7, 4), 5.25)

        db.session.commit()
        trans = db.session.query(Transaction).all()
        assert_equals(len(trans), 2)
        """


