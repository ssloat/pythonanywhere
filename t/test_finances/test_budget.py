from nose.tools import assert_equals
import datetime
import logging


from mysite import db
from finances.budget.models import Budget, Item
from finances.budget.tax_rates import TaxRate
from user.models import User

from base_test import TestBase

class TestBudget(TestBase):

    def setup(self):
        super(TestBudget, self).setup()

        db.session.add( TaxRate('Illinois', 2015, 0, 0, 0.02, 'Single') )
        db.session.add( User(id=1, email='user@host.com', name='test') )

    def test_budget(self):
        b = Budget(1, 'Test', 2015, 'Single')

        Item(b, 'income', 'bofa', 10000, 10000) 
        Item(b, 'pretax', '401k', 500, 1000) 
        

        assert_equals(b.income, 130000)
        assert_equals(b.agi, 123000)
        assert_equals(b.state_tax, 2460)


'''
class TestItem(unittest.TestCase):

    def test_item(self):
        b = Budget('Test', 2015, 'Single')
        item = Item(b, 'income', 'bofa', 10000, 10000)

        assert_equals(item.total, 130000)

'''
 
