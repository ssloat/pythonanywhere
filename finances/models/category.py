from mysite import db

from mysite.models.user import AddUser

class Category(db.Model, AddUser):
    __tablename__ = 'finance_categories'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('finance_categories.id'))
    name = db.Column(db.String(64))
    depth = db.Column(db.Integer, default=0)

    children = db.relationship("Category", 
        backref=db.backref('parent', remote_side=[id])
    )

    def __init__(self, user, name, parent=None, depth=0):
        AddUser.__init__(self, user)
        self.name = name

        if parent:
            self.parent = parent
            self.depth  = parent.depth + 1
        else:
            self.depth = depth

    def tree(self):
        n = {'id': self.id, 'text': self.name}
        if self.children:
            n['children'] = []
            for c in self.children:
                n['children'].append(c.tree())

        return n

    def __repr__(self):
       return "<Category('%s')>" % (self.name)

def categoriesSelectBox(cat=None):
    cat = cat or db.session.query(Category).filter(Category.name=='top').first()
    if cat is None:
        return []

    results = [(cat.id, "".join(cat.depth*['...'] + [cat.name]))]

    for c in cat.children:
        results += categoriesSelectBox(c)

    return results

def allChildren(cat=None):
    if isinstance(cat, int):
        cat = db.session.query(Category).filter(Category.id==cat).first()
        
    cat = cat or db.session.query(Category).filter(Category.name=='top').first()
    results = []
    for c in list(cat.children):
        results.append(c)
        results += allChildren(c)

    return results


