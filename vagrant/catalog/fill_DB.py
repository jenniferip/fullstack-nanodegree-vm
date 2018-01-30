"""
This file pre-fills the database created in catalog_db_setup.py with some
users, categories, and items so that when the user first interacts with the
catalog web application, it is not empty and lack-luster.

However, it is imperative to run this file before running the application as
it initiates all pre-set categories the web application has, as currently
users are not allowed to add a new category.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_db_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


user1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user1)
session.commit()

category1 = Category(name='Latin', user=user1)
session.add(category1)
session.commit()

item1 = Item(title='No Vuelvo Jamas by Carla Morrison',
             description='''A song about losing love but then learning to \
             continue living despite the heartbreak.''', category=category1,
             user=user1)
session.add(item1)
session.commit()


category2 = Category(name='Rap', user=user1)
session.add(category2)
session.commit()

item2 = Item(title='T P O by Dom Kennedy',
             description='''A song about promiscuous women.''',
             category=category2, user=user1)
session.add(item2)
session.commit()


category3 = Category(name='Pop', user=user1)
session.add(category3)
session.commit()

item3 = Item(title='Perfect Duet by Ed Sheeran ft. Beyonce',
             description='''A song about finding the love of your life.''',
             category=category3, user=user1)
session.add(item3)
session.commit()


category4 = Category(name='Country', user=user1)
session.add(category4)
session.commit()

item4 = Item(title='Rich by Marren Morris',
             description='''A song about how rich one would be if given \
             money for everytime they believed in a false love.''',
             category=category4, user=user1)
session.add(item4)
session.commit()

item5 = Item(title='Either Way by Chris Stapleton',
             description='''A song about living with a person who you have \
             fallen out of love with.''', category=category4, user=user1)
session.add(item5)
session.commit()


category5 = Category(name='RnB', user=user1)
session.add(category5)
session.commit()

item6 = Item(title='Come Through and Chill by Miguel ft. J.Cole',
             description='''A song about trying to reconnect for a one night
             stand with a past lover.''', category=category5, user=user1)
session.add(item6)
session.commit()


category6 = Category(name='Rock', user=user1)
session.add(category6)
session.commit()

category7 = Category(name='Folk', user=user1)
session.add(category7)
session.commit()

category8 = Category(name='Soul', user=user1)
session.add(category8)
session.commit()

print 'ADDED ALL ITEMS!'
