from mysite import db


class TaxDeduction(db.Model):
    __tablename__ = 'tax_deductions'

    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(64))
    year     = db.Column(db.Integer)
    amount   = db.Column(db.Integer)
    status   = db.Column(db.String(64))

    def __init__(self, name, year, amount, status=None):
        self.name   = name
        self.year   = year
        self.amount = amount
        self.status = status or 'Single'

    def __repr__(self):
       return "<TaxDeduction('%s', %d, %d, '%s')>" % (
           self.name, self.year, self.amount, self.status
       )

class TaxRate(db.Model):
    __tablename__ = 'tax_rates'

    id     = db.Column(db.Integer, primary_key=True)
    name   = db.Column(db.String(64))
    year   = db.Column(db.Integer)
    start  = db.Column(db.Integer)
    end    = db.Column(db.Integer)
    rate   = db.Column(db.Float)
    status = db.Column(db.String(64))

    def __init__(self, name, year, start, end, rate, status=None):
        self.name   = name
        self.year   = year
        self.start  = start
        self.end    = end
        self.rate   = rate
        self.status = status or 'Single'

    def __repr__(self):
       return "<TaxRate(%s %s %d: %d - %d => %f)>" % (
           self.name, self.status, self.year, self.start, self.end, self.rate,
       )

def tax(tax_rates, amount):
    return reduce(lambda a, b: a + _tax(b, amount), tax_rates, 0.0);

def _tax(tax_rate, amount):
    if tax_rate.start >= amount:
        return 0

    if tax_rate.end == 0 or amount < tax_rate.end:
        return tax_rate.rate * (amount - tax_rate.start)

    return tax_rate.rate * (tax_rate.end - tax_rate.start)

def add_tax_rates(session):
    session.add( TaxDeduction('Fed Standard', 2013, 6100, 'Single') )
    session.add( TaxDeduction('Fed Standard', 2014, 6200, 'Single') )
    session.add( TaxDeduction('Fed Standard', 2015, 6300, 'Single') )

    session.add( TaxDeduction('Fed Standard', 2013, 8950, 'Head') )
    session.add( TaxDeduction('Fed Standard', 2014, 9100, 'Head') )
    session.add( TaxDeduction('Fed Standard', 2015, 9250, 'Head') )

    session.add( TaxDeduction('Fed Standard', 2013, 12200, 'Joint') )
    session.add( TaxDeduction('Fed Standard', 2014, 12400, 'Joint') )
    session.add( TaxDeduction('Fed Standard', 2015, 12600, 'Joint') )

    session.add( TaxDeduction('Fed Standard', 2013, 6100, 'Separate') )
    session.add( TaxDeduction('Fed Standard', 2014, 6200, 'Separate') )
    session.add( TaxDeduction('Fed Standard', 2015, 6300, 'Separate') )

#    session.add( TaxDeduction('401k', 2013, 17000) )
#    session.add( TaxDeduction('401k', 2014, 17500) )
#    session.add( TaxDeduction('401k', 2015, 18000) )

    session.add( TaxRate('Illinois', 2015, 0, 0, 0.0375, 'Single') )
    session.add( TaxRate('Illinois', 2014, 0, 0, 0.05,   'Single') )
    session.add( TaxRate('Illinois', 2013, 0, 0, 0.05,   'Single') )

    session.add( TaxRate('Federal', 2015, 0,      9225,   .10,  'Single') )
    session.add( TaxRate('Federal', 2015, 9225,   37450,  .15,  'Single') )
    session.add( TaxRate('Federal', 2015, 37450,  90750,  .25,  'Single') )
    session.add( TaxRate('Federal', 2015, 90750,  189300, .28,  'Single') )
    session.add( TaxRate('Federal', 2015, 189300, 411500, .33,  'Single') )
    session.add( TaxRate('Federal', 2015, 411500, 413200, .35,  'Single') )
    session.add( TaxRate('Federal', 2015, 413200, 0,      .396, 'Single') )

    session.add( TaxRate('Federal', 2014, 0,      9075,   .10,  'Single') )
    session.add( TaxRate('Federal', 2014, 9075,   36900,  .15,  'Single') )
    session.add( TaxRate('Federal', 2014, 36900,  89350,  .25,  'Single') )
    session.add( TaxRate('Federal', 2014, 89350,  186350, .28,  'Single') )
    session.add( TaxRate('Federal', 2014, 186350, 405100, .33,  'Single') )
    session.add( TaxRate('Federal', 2014, 405100, 406750, .35,  'Single') )
    session.add( TaxRate('Federal', 2014, 406750, 0,      .396, 'Single') )

    session.add( TaxRate('Federal', 2013, 0,      8925,   .10,  'Single') )
    session.add( TaxRate('Federal', 2013, 8925,   36250,  .15,  'Single') )
    session.add( TaxRate('Federal', 2013, 36250,  87850,  .25,  'Single') )
    session.add( TaxRate('Federal', 2013, 87850,  183250, .28,  'Single') )
    session.add( TaxRate('Federal', 2013, 183250, 398350, .33,  'Single') )
    session.add( TaxRate('Federal', 2013, 398350, 400000, .35,  'Single') )
    session.add( TaxRate('Federal', 2013, 400000, 0,      .396, 'Single') )

    session.add( TaxRate('Federal', 2015, 0,      13150,  .10,  'Head') )
    session.add( TaxRate('Federal', 2015, 13150,  50200,  .15,  'Head') )
    session.add( TaxRate('Federal', 2015, 50200,  129600, .25,  'Head') )
    session.add( TaxRate('Federal', 2015, 129600, 209850, .28,  'Head') )
    session.add( TaxRate('Federal', 2015, 209850, 411500, .33,  'Head') )
    session.add( TaxRate('Federal', 2015, 411500, 439000, .35,  'Head') )
    session.add( TaxRate('Federal', 2015, 439000, 0,      .396, 'Head') )

    session.add( TaxRate('Federal', 2014, 0,      12950,  .10,  'Head') )
    session.add( TaxRate('Federal', 2014, 12950,  49400,  .15,  'Head') )
    session.add( TaxRate('Federal', 2014, 49400,  127550, .25,  'Head') )
    session.add( TaxRate('Federal', 2014, 127550, 206600, .28,  'Head') )
    session.add( TaxRate('Federal', 2014, 206600, 405100, .33,  'Head') )
    session.add( TaxRate('Federal', 2014, 405100, 432200, .35,  'Head') )
    session.add( TaxRate('Federal', 2014, 432200, 0,      .396, 'Head') )

    session.add( TaxRate('Federal', 2013, 0,      12750,  .10,  'Head') )
    session.add( TaxRate('Federal', 2013, 12750,  48600,  .15,  'Head') )
    session.add( TaxRate('Federal', 2013, 48600,  125450, .25,  'Head') )
    session.add( TaxRate('Federal', 2013, 125450, 203150, .28,  'Head') )
    session.add( TaxRate('Federal', 2013, 203150, 398359, .33,  'Head') )
    session.add( TaxRate('Federal', 2013, 398359, 425000, .35,  'Head') )
    session.add( TaxRate('Federal', 2013, 425000, 0,      .396, 'Head') )

    session.add( TaxRate('SocialSecurity', 2014, 0, 117000, 0.062) )
    session.add( TaxRate('SocialSecurity', 2015, 0, 118500, 0.062) )

    session.add( TaxRate('Medicare', 2014, 0, 200000, 0.0145, 'Single') )
    session.add( TaxRate('Medicare', 2014, 200000, 0, 0.0235, 'Single') )
    session.add( TaxRate('Medicare', 2014, 0, 250000, 0.0145, 'Joint') )
    session.add( TaxRate('Medicare', 2014, 250000, 0, 0.0235, 'Joint') )
    session.add( TaxRate('Medicare', 2014, 0, 125000, 0.0145, 'Separate') )
    session.add( TaxRate('Medicare', 2014, 125000, 0, 0.0235, 'Separate') )

    session.add( TaxRate('Medicare', 2015, 0, 200000, 0.0145, 'Single') )
    session.add( TaxRate('Medicare', 2015, 200000, 0, 0.0235, 'Single') )
    session.add( TaxRate('Medicare', 2015, 0, 250000, 0.0145, 'Joint') )
    session.add( TaxRate('Medicare', 2015, 250000, 0, 0.0235, 'Joint') )
    session.add( TaxRate('Medicare', 2015, 0, 125000, 0.0145, 'Separate') )
    session.add( TaxRate('Medicare', 2015, 125000, 0, 0.0235, 'Separate') )

    session.commit()
