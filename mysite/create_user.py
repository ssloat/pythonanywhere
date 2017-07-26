from mysite import db

from mysite.models.user import User, ProviderId
from finances.models.category import Category

def create_user(social_id, first_name, last_name, email):
    user = User(
        first_name=first_name,
        last_name=last_name,
        name=' '.join([first_name, last_name]),
        email=email
    )
    provider_id = ProviderId(id=social_id, user=user)
    db.session.add(user)
    db.session.add(provider_id)

    top = Category(user, 'top')
    uncat = Category(user, 'uncategorized', top)
    db.session.add(top)
    db.session.add(uncat)

    db.session.commit()
    return user
 
