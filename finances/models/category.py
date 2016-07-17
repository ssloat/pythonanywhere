from mysite import db

from mysite.user.models import AddUser

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
        self.name   = name

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
 
class CategoryRE(db.Model, AddUser):
    __tablename__ = 'finance_category_res'

    id = db.Column(db.Integer, primary_key=True)
    pattern = db.Column(db.String(64))
    minimum = db.Column(db.Float, nullable=True)
    maximum = db.Column(db.Float, nullable=True)

    actions = db.relationship("Action")

    def __init__(self, user, pattern, minimum=None, maximum=None):
        AddUser.__init__(self, user)

        self.pattern = pattern
        self.minimum = minimum
        self.maximum = maximum

    def __repr__(self):
       return "<CategoryRE('%s')>" % (self.pattern)

class Action(db.Model, AddUser):
    __tablename__ = 'finance_actions'

    id = db.Column(db.Integer, primary_key=True)
    categoryre_id = db.Column(db.Integer, db.ForeignKey('finance_category_res.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('finance_categories.id'))
    name = db.Column(db.String(64))
    yearly = db.Column(db.Boolean, default=False)
    fixed = db.Column(db.Float, nullable=True)

    category = db.relationship("Category")

    def __init__(self, name, categoryre, category, yearly=False, fixed=None):
        AddUser.__init__(self, user)

        self.name = name
        self.yearly = yearly
        self.fixed = fixed

        if isinstance(categoryre, int):
            self.categoryre_id = categoryre
        else:
            self.categoryre_id = categoryre.id

        if isinstance(category, int):
            self.category_id = category
        else:
            self.category = category



def create_categories():
    top = Category('top', None, 0)

    jnl = Category('journal', top)
    boachk = Category('bofa chk', jnl)

    trans = Category('transactions', top)

    _401k = Category('401k', trans)

    bofa     = Category('bofa', trans)
    inc      = Category('bofa income', bofa)
    taxes    = Category('inc taxes', bofa)
    pretax   = Category('preTax', bofa)
    match    = Category('401k match', bofa)

    give      = Category('giving', trans)
    rez       = Category('rez', give)
    comp_intl = Category('comp intl', give)
    gfa       = Category('gfa', give)
    keith     = Category('keith', give)
    stanley   = Category('stanley', give)
    keane     = Category('keane', give)
    stott     = Category('stott', give)
    stars     = Category('stars', give)

    house     = Category('house', trans)
    rent      = Category('rent', house)
    mort      = Category('mortgage', house)
    mort_int  = Category('mortgage int', mort)
    mort_prin = Category('mortgage prin', mort)
    htax      = Category('property tax', house)
    hrep      = Category('house maint', house)
    utils     = Category('house utilities', house)
    h_ins     = Category('house insurance', house)

    budget   = Category('budget', trans)
    monthly  = Category('monthly', budget)

    car      = Category('car', budget)
    kona     = Category('kona', budget)
    ent      = Category('entertainment', budget)
    group    = Category('group outing', ent)
    amazon   = Category('amazon', ent)
    movies   = Category('movies', ent)
    sports   = Category('sports', ent)

    food     = Category('food', budget)
    fin      = Category('food in', food)
    fout     = Category('food out', food)
    fogroup  = Category('fo group', fout)
    fosolo   = Category('fo solo', fout)

    uncat    = Category('uncategorized', budget)
    chks     = Category('checks', uncat)
    clothes  = Category('clothes', uncat)
    cash     = Category('cash', uncat)
    girl     = Category('girl', budget)
    dates    = Category('dates', girl)
    presents = Category('presents', girl)
    travel   = Category('travel', budget)

    nontaxable = Category('nontaxable income', trans)

    db.session.add_all([top, 
        jnl, boachk, _401k,
        trans,
        bofa, inc, taxes, pretax, match,
        give, 
        house, rent, mort, mort_int, mort_prin, htax, hrep, utils, h_ins,
        budget, monthly, 
        car, kona, ent, group, amazon, movies, sports, 
        food, fin, fout, fogroup, fosolo, 
        uncat, chks, clothes, cash, girl, dates, presents, travel,
        nontaxable,
    ])

    db.session.commit()


def allChildren(cat=None):
    cat = cat or db.session.query(Category).filter(Category.name=='top').first()
    results = []
    for c in list(cat.children):
        results.append(c)
        results += allChildren(c)

    return results

