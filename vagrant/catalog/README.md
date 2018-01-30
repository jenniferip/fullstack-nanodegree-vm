# Jennifer Penuelas' Item Catalog Project

`/catalog` is a directory containing two subdirectories `/static` and `/templates` which contain stylesheets and html code to render the item catalog web app, respectively, and also contains the necessary files to implement a database backed web application using the Flask framework and SQLAlchemy package for creating and querying a database.

This application works in that you can loggin, using Google+, and add, edit, and delete items from a list of categories with the exceptions that if you cannot edit or delete an item that you did not create.

Please note, the code for this web application was modeled with Udacity's 'The Backend: Databases and Applications` lesson in mind. Some code, particularly the code implementing Google+ authentication and authorication, is almost exactly the same with the understanding of the concepts.  

## How to run 

Since, this web application is currently run through my own local computer no one else can access it using some internet accessible URL. Instead, to run the application, you will have to run `python application.py` from the terminal to run the web application that you can play with in the browser.

Once you have the application running, you will see the terminal start to output HTTP messages. Then you can access the web application from the browser with the following url: `http://localhost:8000/catalogs`.

**NOTE: Before doing any of the above steps, you may have to start up the virtual machine. I used the vagrant virtual machine, to run it do `vagrant up` in your terminal and then `vagrant ssh`. Once you have the virtual machine running, you will want to enter the `/catalog` directory from within the virtual machine by doing `cd /vagrant/catalog`.**

## Files

The files and folders included are:

* `application.py` - this file contains all of the necessary code to have a functioning web application that is backed by a database. It implements all code to login using an outside authorization and authentication service, implements all of the code for the user to implement CRUD operations through the web app, and implements the necessary code to implement API endpoints ie. recieve a JSON document of whatever information the user may ask for.

* `catalog_db_setup.py` - this file contains all of the code to initiate the database, called `itemcatalog.db`, necessary for the catalog web app. It defines all tables of the database. I have already ran this along with the `fill_DB.py` file so the database is already created. In case it is not, ie. you do not see a `itemcatalog.db` file in the catalog zip you will have to run this file by typing `python catalog_db_setup.py` in the terminal then `python fill_db.py` before initiating the application as in the 'How to Run' section.

* `fill_DB.py` - fills the database created by `catalog_db_setup.py` with some initial users, categories, and items so that the web app looks a little more interesting when you first open it. Additionally, you must run this file because it creates the pre-established categories, as this web app currently does not allow the user to create their own categories. Please look to `catalog_db_setup.py`'s information in case the application does not seem to be working with a database...could be the `itemcatalod.db` is not included.

* `client_secrets.json` - this is a file not important to user or the person running this application, it contains information necessary to implement the authentication and authorization, using the outside source.

* `README.txt`

* `/static`:
	> * `style.css` - this contains extra styling for my web application, it mostly handles positioning as I used bootstrap to do more of the coloring.

* `/templates`:
	> * `addItem.html` - all HTML code to render the webpage to add a new item, it extends the `main.html` file.

	> * `aside.html` - the HTML code to render the list of categories as an aside that is always present while on the web app, it extends `main.html`.

	> * `catalogs.html` - HTML code that extends `main.html`. It renders the main page of the catalog web app with the aside and the lates items added.

	> * `category.html` - renders the page for a specific category, lists all items within that category, extends `main.html`.

	> * `deleteItem.html` - HTML code to render the page to possibly delete a specific item, extends `main.html`.

	> * `editItem.html` - HTML code to render the page to possibly edit a specific item, extends `main.html`.

	> * `header.html` - the HTML code to render the login/logout and the 'Go to Main` buttons in the header of the web app. It is always present and extends `main.html`.

	> * `item.html` - the HMTL code to render the webpage of a particular item, it extends `main.html`.

	> * `login.html` - HTML code to implement the Google+ login functionality.

	> * `main.html` - HTML code to start off the webpage. It actually does not contain much information outside of the <head> tag's links to the stylesheets, as all pages are built on separate html documents that extend this file.

	> * `publicCatalog.html` - read the information for `catalogs.html` above, this page does the same however, it does not include the option to add an item in the main page which is included when the user is logged into the site.

	> * `publicCategory.html` - similar to `category.html` however where `category.html` displays an option to add an item, this file does not have that option for those not logged in.

	> * `publicItem.html` - same as `item.html` except this one renders when the user is not logged into the web application thus, not giving the user the options to edit or delete the particular item.
