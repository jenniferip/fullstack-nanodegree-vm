"""
This file contains all code necessary to implement all functionality of the
catalog web application, including: the google plus login authentication and
authorization, all CRUD operations that act on the database itemcatalog.db,
and finally the API endpoints.
"""

from flask import Flask, render_template, request, redirect, jsonify, \
    url_for, flash
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker
from catalog_db_setup import Base, Category, Item, User

# New imports to create anti forgery state token
from flask import session as login_session
import random
import string

# Imports for GConnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
CLIENT_ID = json.loads(
                 open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Catalog App'

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


##############################################################################
# THIS NEXT PORTION OF THIS CODE IMPLEMENTS ALL AUTHENTICATION AND           #
# AUTHORIZATION, USING GOOGLE PLUS. ADDITIONALLY THERE ARE SOME HELPER       #
# METHODS FOR THE LOGIN USING GOOGLE PLUS. THESE ARE:                        #
# createUser(login_session), getUserInfo(user_id), and getUserId(email)      #
##############################################################################
@app.route('/login')
def showLogin():
    """
    Create a state token to prevent forgery and store it in the session for
    later validation.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    This function implements all code to log in to the web application using
    Google Plus and then create a user within the web applications database.
    Note: much of this code is taken from Udacity's 'The Backend: Databases
    and Applications' lessons.
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserId(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """ " style = "width: 300px; height: 300px;border-radius: \
                  150px;-webkit-border-radius: 150px;-moz-border-radius: \
                  150px;"> """
    flash("You are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """
    This function is the current acting function to log out of the web
    application. Again, much of this code is similar to that from Udacity's
    'The Backend: Databases and Applications'.
    """
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        flash('You Have Successfully Logged Out')
        return redirect(url_for('showCatalogMain'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        flash('Log Out was Unsuccessful')
        return redirect(url_for('showCatalogMain'))


@app.route('/disconnect')
def disconnect():
    """
    This function is currently not active, however it generalizes the log out
    process for the web application so that we can expand the log in using
    multiple auth providers. At which point, we check the current login
    session's provider and call its specific log out function from within this
    function.
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalogMain'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalogMain'))


def createUser(login_session):
    """
    This function is a helper function to gconnect(). It is called within that
    function to create a user in our database.
    """
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    This function is a helper function to gconnect(). It returns the user
    object correlating with the user that is trying to log in.
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user_id


def getUserId(email):
    """
    Another helper function to gconnect(), getUserId() returns the user id of
    the user attempting to log in, if the user exists.
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


##############################################################################
# FROM THIS POINT ONTO THE NEXT COMMENT SECTION THE CODE IMPLEMENTS HOW THE  #
# WEB APPLICATION RENDERS AND TAKES CARE OF IMPLEMENTING ALL CRUD OPERATIONS #
##############################################################################
@app.route('/')
@app.route('/catalogs/')
def showCatalogMain():
    """
    This function renders either the public catalog main page or the catalog
    main page for when a user is logged in, allowing the user to add an item
    from this page.
    """
    categories = session.query(Category).all()
    latest = session.query(Item).order_by(desc(Item.time_created)).limit(7)
    if 'username' not in login_session:
        return render_template('publicCatalogs.html', categories=categories,
                               latest_items=latest)
    return render_template('catalogs.html', categories=categories,
                           latest_items=latest)


@app.route('/catalog/<int:category_id>/')
def showCategory(category_id):
    """
    This function renders either the public page for a particular category or
    the page for a particular category when a user is logged in, allowing the
    user to add an item from this page.
    """
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    category_items = session.query(Item).filter_by(category=category)
    if 'username' not in login_session:
        return render_template('publicCategory.html', category=category,
                               category_items=category_items,
                               categories=categories)
    else:
        return render_template('category.html', category=category,
                               category_items=category_items,
                               categories=categories)


@app.route('/catalog/<int:category_id>/<int:item_id>/')
def showItem(category_id, item_id):
    """
    This function renders either the public page for a particular item or
    the page for a particular item when a user is logged in, which gives the
    user the options to edit or delete the particular item.
    """
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()
    creator = session.query(User).filter_by(id=item.user_id).one()
    if 'username' not in login_session:
        return render_template('publicItem.html', item=item, creator=creator,
                               categories=categories)
    else:
        return render_template('item.html', item=item, creator=creator,
                               categories=categories)


@app.route('/catalog/<int:category_id>/new/', methods=['GET', 'POST'])
def addItem(category_id):
    """
    This function renders the page to add an item but only if the current user
    is logged in, otherwise it redirects the user to log in.
    """
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Item(title=request.form['title'],
                       description=request.form['description'],
                       category=session.query(Category).filter_by(
                                name=request.form['category']).one(),
                       user=session.query(User).filter_by(
                                id=login_session['user_id']).one())
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Created' % newItem.title)
        return redirect(url_for('showCatalogMain'))
    else:
        return render_template('addItem.html', category_id=category_id,
                               categories=categories)


@app.route('/catalog/<int:category_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """
    This function renders the page to edit an item but only if the current
    user created the item and is logged in. If the user is not the user who
    created the item, the function redirects them to the showItem page and
    flashes them a message informing them that they cannot edit this item. If
    the user is not logged in, it redirects the user to log in.
    """
    categories = session.query(Category).all()
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedItem.user_id != login_session['user_id']:
        flash("""You are not authorized to edit this item. Please create \
            your own item in order to edit.""")
        return redirect(url_for('showItem', category_id=category_id,
                        item_id=item_id))
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category = session.query(Category).filter_by(
                name=request.form['category']).one()
        session.add(editedItem)
        session.commit()
        flash('Item %s Successfully Edited' % editedItem.title)
        return redirect(url_for('showCatalogMain'))
    else:
        return render_template('editItem.html', category_id=category_id,
                               item_id=item_id, item=editedItem)


@app.route('/catalog/<int:category_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    """
    This function renders the page to delete an item but only if the current
    user created the item and is logged in, otherwise it either redirects the
    user to show the item and flashes them a message or redirects the user to
    log in, respectively.
    """
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if itemToDelete.user_id != login_session['user_id']:
        flash("You are not authorized to delete this item.")
        return redirect(url_for('showItem', category_id=category_id,
                                item_id=item_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item %s Successfully Deleted' % itemToDelete.title)
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete,
                               categories=categories)


##############################################################################
# LASTLY, THIS BIT OF CODE IMPLEMENTS ALL API ENDPOINTS SO THAT A USER IS    #
# ABLE TO GET ALL INFORMATION AS A JSON FORMAT                               #
##############################################################################
@app.route('/catalogs/JSON/')
@app.route('/catalog/JSON/')
def catalogsJSON():
    """
    This function gives the JSON information for all categories.
    """
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


@app.route('/catalog/<int:category_id>/JSON/')
def categoryJSON(category_id):
    """
    This function gives the JSON information for all items within a category.
    """
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category=category).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/<int:category_id>/<int:item_id>/JSON/')
def itemJSON(category_id, item_id):
    """
    This function gives the JSON information for a particular item.
    """
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'temp_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
