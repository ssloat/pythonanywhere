from mysite import app

from flask import render_template
from flask.ext.login import current_user


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')



