from nose.tools import assert_equals


from mysite import db
from finances.models.category import Category, categoriesSelectBox

from t.base_test import TestBase

class TestCategory(TestBase):

    def setUp(self):
        super(TestCategory, self).setUp()

        def create_category(*args):
            c = Category(self.user, *args)
            db.session.add(c)
            db.session.commit()
            return c

        top = create_category('top', None, 0)
        child = create_category('child', top)
        gchild = create_category('grandchild', child)
        uncat = create_category('uncategorized', top)


    def test_category(self):
        child = db.session.query(Category).filter(Category.name=='child').first()

        assert_equals(child.name, 'child')
        assert_equals(child.parent.name, 'top')
        assert_equals(len(child.children), 1)

        top = db.session.query(Category).filter(Category.name=='top').first()
        tree = top.tree()
        assert_equals(len(tree['children']), 2)
        
        child = filter(lambda x: x['text']=='child', tree['children'])[0]
        assert_equals(len(child['children']), 1)

    def test_select_box(self):
        expected = [
            (1, 'top'),
            (2, '...child'),
            (3, '......grandchild'),
            (4, '...uncategorized'),
        ]

        assert_equals(categoriesSelectBox(), expected)


