"""BirdGrip Website"""
"""("grip" is birder slang for bragging about one's sightings)"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import Bird, connect_to_db, db

app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "TINAMOU"

app.jinja_env.undefined = StrictUndefined

# Housekeeping over. Now for routes.

@app.route('/')
def index():
    """Homepage."""

    orders = Bird.query.order_by(Bird.taxon_id).group_by(Bird.order).all()
    birds = Bird.query.order_by(Bird.taxon_id).all()
    
    for order in orders:
        print order.order

    # bird_output_list = []

    # for bird in birds:
    # 	taxon_id = bird.taxon_id
    # 	sci_name = bird.sci_name
    #     family = bird.family
    #     order = bird.order
    # 	com_name = bird.common_name

    # 	bird_output_list.append((taxon_id, sci_name, com_name, family, order))



    return render_template("homepage.html", orders=orders, birds=birds)

@app.route('/search')
def search():
	pass

@app.route('/login')
def login():
	pass

@app.route('/logout')
def logout():
	pass



# Stuff I didn't write that makes the app go.
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()