from flask.ext.wtf import Form
from wtforms import TextField, SelectField, SubmitField

from finances.models.category import Category
from mysite import db

class NewCategoryForm(Form):
    name = TextField('Name')
    parent = SelectField('Parent', coerce=int)
    submit = SubmitField('Submit')

    def process_input(self, cats):
        cat = Category(self.name.data, cats[self.parent.data]) 
        db.session.add( cat )
        db.session.commit()

        self.parent.choices.append((cat.id, cat.name))
        self.name.data = ""
        self.parent.data = 1


