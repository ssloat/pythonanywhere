from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, SubmitField

from mysite import db
from finances.models.category import Category

class NewCategoryForm(FlaskForm):
    name = TextField('Name')
    parent = SelectField('Parent', coerce=int)
    submit = SubmitField('Submit')

    def process_input(self, user_id, cats):
        cat = Category(
            user_id, self.name.data, cats[self.parent.data]
        ) 
        db.session.add( cat )
        db.session.commit()

        self.name.data = ""
        self.parent.data = 1



