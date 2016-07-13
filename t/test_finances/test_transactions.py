from nose.tools import assert_equals
import datetime
import logging


from mysite import db
from finances.transaction.models import Transaction, Category, CategoryRE, Action, create_categories

from base_test import TestBase

class TestTransaction(TestBase):

    def setUp(self):
        super(TestTransaction, self).setUp()

        top = Category('top', None, 0)
        child = Category('child', top)
        gchild = Category('grandchild', child)

        pattern = CategoryRE('pattern')
        db.session.add(pattern)
        db.session.commit()

        action1 = Action('one', pattern, gchild)
        action2 = Action('two', pattern, gchild, yearly=True)

        db.session.add_all([top, child, gchild, pattern, action1, action2])


    def test_category(self):
        child = db.session.query(Category).filter(Category.name=='child').first()

        assert_equals(child.name, 'child')
        assert_equals(child.parent.name, 'top')
        assert_equals(len(child.children), 1)

        pattern = db.session.query(CategoryRE).first()
        for action, id in zip(pattern.actions, ('a', 'b')):
            action.load(id, datetime.date(2016, 7, 4), 5.25)

        db.session.commit()
        trans = db.session.query(Transaction).all()
        assert_equals(len(trans), 2)


