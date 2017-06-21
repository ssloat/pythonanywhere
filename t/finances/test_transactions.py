from nose.tools import assert_equals
import datetime
import logging


from mysite import db
from finances.models.transaction import Transaction, parse_ofx
from finances.models.category import Category
from finances.models.pattern import Pattern, Action

from t.base_test import TestBase

def create_category(user, *args):
    c = Category(user, *args)
    db.session.add(c)
    db.session.commit()
    return c

class TestTransaction(TestBase):

    def setUp(self):
        super(TestTransaction, self).setUp()

        top = create_category(self.user, 'top', None, 0)
        child = create_category(self.user, 'child', top)
        gchild = create_category(self.user, 'grandchild', child)
        uncat = create_category(self.user, 'uncategorized', top)

        pattern = Pattern(self.user, 'pattern')
        db.session.add(pattern)
        db.session.commit()

        action1 = Action(self.user, 'one', pattern, gchild)
        action2 = Action(self.user, 'two', pattern, gchild, yearly=True)

        db.session.add_all([pattern, action1, action2])


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

class TestUploadTransactions(TestBase):
    def setUp(self):
        super(TestUploadTransactions, self).setUp()

        top = create_category(self.user, 'top', None, 0)
        child = create_category(self.user, 'child', top)
        gchild = create_category(self.user, 'grandchild', child)
        uncat = create_category(self.user, 'uncategorized', top)

        pattern = Pattern(self.user, 'JEWEL')
        db.session.add(pattern)
        db.session.commit()

        action1 = Action(self.user, 'one', pattern, gchild)
        action2 = Action(self.user, 'two', pattern, gchild, yearly=True)

        db.session.add_all([pattern, action1, action2])

    def test_one_match(self):
        results = parse_ofx(self.user, ONE_MATCH)
        self.assertEquals(len(results['transactions']), 2)
        self.assertEquals(len(results['uncategorized']), 0)


ONE_MATCH = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0
                <SEVERITY>INFO
            </STATUS>
            <DTSERVER>20170527150022[0:UTC]
            <LANGUAGE>ENG
            <FI>
                <ORG>Bank of America
                <FID>5959
            </FI>
            <INTU.BID>6526
        </SONRS>
    </SIGNONMSGSRSV1>
    <CREDITCARDMSGSRSV1>
        <CCSTMTTRNRS>
            <TRNUID>20170527150022[0:UTC]
            <STATUS>
                <CODE>0
                <SEVERITY>INFO
            </STATUS>
            <CCSTMTRS>
                <CURDEF>USD
                <CCACCTFROM>
                    <ACCTID>4400668319487841
                </CCACCTFROM>
                <BANKTRANLIST>
                    <DTSTART>20170417160000[0:UTC]
                    <DTEND>20170516160000[0:UTC]
                    <STMTTRN>
                        <TRNTYPE>PAYMENT
                        <DTPOSTED>20170417160000[0:UTC]
                        <TRNAMT>-30.86
                        <FITID>201704171
                        <CORRECTFITID>201704171
                        <CORRECTACTION>REPLACE
                        <NAME>JEWEL #3340 GLEN ELLYN IL
                    </STMTTRN>
                </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>-1151.21
                    <DTASOF>20170516000000[0:UTC]
                </LEDGERBAL>
            </CCSTMTRS>
        </CCSTMTTRNRS>
    </CREDITCARDMSGSRSV1>
</OFX> 
"""
