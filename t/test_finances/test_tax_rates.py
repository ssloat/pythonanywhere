from nose.tools import assert_equals
import datetime

from finances.budget.tax_rates import TaxRate, _tax, tax

def test__tax():
    tax_rates = [ 
        TaxRate('Federal', 2014, 0,      9000,  .10,  'Single'),
        TaxRate('Federal', 2014, 9000,   19000, .15,  'Single'),
        TaxRate('Federal', 2014, 19000,  0,     .25,  'Single'),
    ]

    assert_equals(_tax(tax_rates[1], 9000), 0)
    assert_equals(_tax(tax_rates[0], 9000), 900)
    assert_equals(_tax(tax_rates[1], 19000), 1500)
    assert_equals(_tax(tax_rates[1], 29000), 1500)
    assert_equals(_tax(tax_rates[2], 29000), 2500)

def test_tax():
    tax_rates = [ 
        TaxRate('Federal', 2014, 0,      9000,  .10,  'Single'),
        TaxRate('Federal', 2014, 9000,   19000, .15,  'Single'),
        TaxRate('Federal', 2014, 19000,  0,     .25,  'Single'),
    ]

    assert_equals(tax(tax_rates, 29000), 900+1500+2500)
 
