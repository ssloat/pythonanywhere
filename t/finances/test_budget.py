from nose.tools import assert_equals
import datetime
import logging


from mysite import db
from finances.models.budget import Budget, Item
from finances.models.tax_rates import TaxRate

from t.base_test import TestBase

class TestBudget(TestBase):

    def setUp(self):
        super(TestBudget, self).setUp()

        db.session.add( TaxRate('Illinois', 2015, 0, 0, 0.02, 'Single') )

    def test_budget(self):
        b = Budget(self.user, 'Test', 2015, 'Single')

        Item(b, 'income', 'bofa', 10000, 10000) 
        Item(b, 'pretax', '401k', 500, 1000) 
        

        assert_equals(b.income, 130000)
        assert_equals(b.agi, 123000)
        assert_equals(b.state_tax, 2460)


