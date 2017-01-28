from flask_wtf import Form
from wtforms import TextField, SubmitField

class NewBudgetForm(Form):
    name = TextField('Name')
    year = TextField('Year')
    status = TextField('Status')
    submit = SubmitField('Submit')

