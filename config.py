import os
basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'super_secret_key'
OAUTH_CREDENTIALS = {
#    'facebook': {
#        'id': '159902947720198',
#        'secret': '421f7885e4fa79c9f994154d8174eec7',
#    },

    #dev
    'facebook': {
        'id': '159908724386287',
        'secret': '140b6e585551a46993d8ff9e88d17e93',
    },
    'twitter': {
        'id': 'BvWWDcShn8nQZe3KcUqtQpYAJ',
        'secret': 'JtRL8fyry9Uf1DfWM0B0oKiuJ7KDTyTquCU7ViY1WhaBzcipb1',
    }
}

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')


