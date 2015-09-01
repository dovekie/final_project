"""Lek website"""

# Imports from Python libraries
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify, url_for, g 
from flask_debugtoolbar import DebugToolbarExtension
from json import dumps, loads
import requests
from flask_oauth import OAuth
import os
import twitter
from constants import *
from datetime import datetime

# Imports from local scripts
from model import User, Bird, Observation, UserSearch, connect_to_db, db
from searchbirds import birdsearch
import tests

# Create a Flask instance
app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "TINAMOU"

# Make jinja go.
app.jinja_env.undefined = StrictUndefined

# If the server runs in a context where it can get the environment variables, use them.
# Otherwise, import variables from a file.
try:
    consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
    access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
except KeyError:
    from sos import *


# Connect to the Twitter API
api = twitter.Api(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token_key=access_token_key,
    access_token_secret=access_token_secret)
oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=consumer_key,
    consumer_secret=consumer_secret)
@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')


# Housekeeping over. Now for routes.
##############################################################################
# HOMEPAGE ROUTES

@app.route('/test')
def test():
    """
    Takes no input. Returns a string.

    This route establishes a baseline for unittests.
    """
    
    this_user_id = 4
    bird_ids_list = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id).all()
    bird_ids = [bird_id[0].encode('ascii', 'ignore') for bird_id in bird_ids_list]

    bird_info_dict = {}
    for bird_id in bird_ids:
        bird_info = db.session.query(Bird.common_name, Bird.sci_name).filter(Bird.taxon_id == bird_id).first()
        bird_info_dict[bird_id] = bird_info

    print bird_info_dict

    return "I test! I fail! I test again!"

@app.route('/')
def index():
    """
    Display the home page with a dynamic list of bird species organized by order and family.

    Gets userid from the session variable and checks for a default search string.
    If a default exists, fetches it and customizes the data displayed on the page.
    """
    # get the list of spuh
    spuh = SPUH_EQUIVALENTS

    # if the user is logged in, this will return their ID
    this_user_id = session.get('user_id', None)                               

    # If the user is not logged in, call birdsearch with no arguments
    # Display the default: all birds.
    # If the user is logged in, fetch their default search from the database
    # Display their custom page
    if this_user_id is None:
        print "Homepage rendering with no user default: User not logged in."
        bird_dict = birdsearch()
    else:
        # Database query
        user_default = UserSearch.query.filter(UserSearch.user_id == this_user_id, 
                                                   UserSearch.user_default == True).first()
        if user_default:
            # Split the serialized search string on & to get paramater/value pairs in strings
            param_list = user_default.search_string.split("&")
            # Create a dictionary by splitting those pairs on =
            search_dict = {param.split("=")[0]: param.split("=")[1] for param in param_list}
            
            print "user default search>>>", search_dict
            # Call birdsearch with the user's custom search parameters
            bird_dict = birdsearch(this_user_id, 
                                  search_dict["which_birds"], 
                                  search_dict["select_spuh"], 
                                  search_dict["select_order"], 
                                  search_dict["select_family"], 
                                  search_dict["select_region"])
        # otherwise, show the generic page                                                           
        else:
            print "Homepage rendering with no user default: User has no default set"
            bird_dict = birdsearch()

    return render_template("homepage.html", birds_nest=bird_dict["birds_dict"], orders=bird_dict["orders"], spuh=spuh)

@app.route('/lifelist')
def lifelist():
    """
    Display all birds that the user has marked as 'seen'

    Only logged-in users should see this page.
    """

    spuh = SPUH_EQUIVALENTS
    user_id = session.get('user_id', None)
    print "lifelist user id:", user_id    

    # Call birdsearch with this user's ID and the parameter that shows their birds only.
    bird_dict = birdsearch(this_user_id=user_id, bird_limit = "my_birds")

    return render_template("homepage.html", birds_nest=bird_dict["birds_dict"], orders=bird_dict["orders"], spuh=spuh)

@app.route('/show_all')
def show_all():
    """
    Show all bird with one button click
    """

    spuh = SPUH_EQUIVALENTS
    # Call birdsearch with no arguments.
    bird_dict = birdsearch()
    return render_template("homepage.html", birds_nest=bird_dict["birds_dict"], orders=bird_dict["orders"], spuh=spuh)

@app.route('/bird_gallery')
def bird_gallery():
    """
    Display pictures with links from ARKive of all birds seen by the user

    Takes the user id and queries the database for bird ids in the observations table
    This route queries the database directly. It gets bird ids only.
    This route should only be seen by logged-in users.
    """

    this_user_id = session.get('user_id', None)
    bird_info_dict = {}
    # get a list of the user's observations from the db IDs ONLY
    if this_user_id:                                                                
        bird_ids_list = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id).all()

        # Create a list of ASCII-encoded bird ids
        bird_ids = [bird_id[0].encode('ascii', 'ignore') for bird_id in bird_ids_list]
        bird_ids.sort()
        for bird_id in bird_ids:
            bird_info = db.session.query(Bird.common_name, Bird.sci_name).filter(Bird.taxon_id == bird_id).first()
            bird_info_dict[bird_id] = bird_info
    else:
        flash("Please log in to view your bird gallery.")

    print bird_info_dict

    return render_template("gallery.html", bird_ids=bird_info_dict)

@app.route('/bird_pictures')
def bird_pictures():
    """
    This route responds to an AJAX request. It calls the ARKive API and returns an HTML string.

    This route queries the database directly. It gets a specific bird's scientific name by ID.
    This route has no view.
    """

    # The ARKive API URL
    base_url = "http://www.arkive.org/api/KjJPGXLFF6CLL5FOvk_Lx8JRvSuBJH1R1tmoGXFrYcE1/portlet/latin/%s/1"

    # Get the bird id from the AJAX request
    bird_request = request.args.get('bird_id').encode('ascii', 'ignore')
    print "ARKive API call for bird ID:", bird_request

    # Strip non-id characters
    this_bird_id = bird_request.lstrip('photo_')

    # Query the database for this bird ID's scientific name
    obs_list = db.session.query(Bird.sci_name).filter(Bird.taxon_id == this_bird_id).first()

    # Extract ascii-encoded text from tuple
    bird_name = obs_list[0].encode('ascii', 'ignore')
    print "Bird name:", bird_name

    # Insert the scientific name into the base URL. This allows spaces.
    target_url = base_url %bird_name

    # Attempt to get the API response
    ark_response = requests.get(target_url)
    ark_status = ark_response.status_code

    # If the ARKive API responds, create a dictionary with the HTML returned by the API
    # Then JSONify the dictionary
    # Otherwise create a dictionary with an empty span and JSONIFY that.
    if ark_status == 200:
        print "ARKive status 200!"
        ark_response_data = dumps({'id': bird_request, 'uri': loads(ark_response.text)['results'][0].encode('ascii', 'ignore')})
    else:
        print "%s not found in ARKive." %bird_name
        ark_response_data = dumps({'id': bird_request, 'uri': '<span></span>'})

    return ark_response_data

@app.route('/mark_user_birds', methods=["GET"])
def mark_birds():
    """
    This route responds to an AJAX request. It returns a set of birds seen by the user.

    This route queries the database directly. It gets bird ids only.
    """
    # This will return None if the user is not logged in
    this_user_id = session.get('user_id')                               

    # If the user is logged in, querie the database for birds they have marked as seen.
    # Return a set of those birds' IDs
    if this_user_id is not None:
        # get a list of the user's observations from the DB
        obs_list = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id).all()

         # clean up one-item tuples
        obs_dict = {obs[0]: '' for obs in obs_list}

        # make a json string for the AJAX call
        obs_json = jsonify(obs_dict)                                   
        return obs_json
    else:
        return jsonify({})

@app.route('/birdcount', methods=["GET"])
def birdcount():
    """
    This route responds to an AJAX request.
    It query the database for the total number of rows in the observation table with that user's ID on them.
    This route returns a string.

    This route queries the database directly. It gets an integer.
    """

    this_user_id = session.get('user_id')                               

    if this_user_id:
        count = Observation.query.filter_by(user_id = this_user_id).count()

        # AJAX only takes strings.
        return str(count)
    else:
        return str(0)

##############################################################################
# SEARCH ROUTES

@app.route('/search', methods=["GET"])
def search():
    """
    This displays the search form. It takes no arguments.

    This route uses variables imported from another file.
    """
    # get the SPUH and REGION dictionaries
    spuh = SPUH_EQUIVALENTS
    regions = REGION_CODES

    # Call birdsearch with no arguments to return all birds.
    bird_dict = birdsearch()                                                                             

    return render_template("search.html", orders=bird_dict["orders"], birds_nest = bird_dict["birds_dict"], regions=regions, spuh=spuh)

@app.route('/search', methods=["POST"])
def search_results():
    """
    Search form input.

    Pass user input strings to birdsearch. Also pass the user's ID if the user is logged in.
    Use the results from birdsearch to rerender the homepage.
    """
    
    spuh = SPUH_EQUIVALENTS
    # get the user's id
    this_user_id = session.get('user_id')

    # get the user's search variables
    bird_limit_param = request.form.get("which_birds")
    spuh_param = request.form.get("select_spuh")
    order_param = request.form.get("select_order")
    family_param = request.form.get("select_family")
    region_param = request.form.get("select_region")
    other_param = request.form.get("fuzzy")

    # pass everything to birdsearch, which returns a dictionary
    bird_dict = birdsearch(this_user_id = this_user_id,
                           bird_limit = bird_limit_param,
                           spuh = spuh_param, 
                           order = order_param, 
                           family = family_param,
                           region = region_param)


    # use the birdsearch dictionary to render the home page
    return render_template("homepage.html", birds_nest=bird_dict["birds_dict"], orders=bird_dict["orders"], spuh=spuh)

@app.route('/add_search', methods=["POST"])
def add_search():
    """
    This route responds to an AJAX request.
    Allows the user to save a search string into the database.

    Returns nothing. Returns an empty JSON string to prevent errors.
    """
    print "Saving a new user search."

    # Get the user's id
    this_user_id = session.get('user_id', None)

    if this_user_id is not None:
        # might be able to take this out. It sets a default for the is_default value in the table
        # By default, saved searches are not set as user's default search.
        is_default = 0

        # get the stringified form from the AJAX request. Encode as ascii.
        search_string = request.form.get('search_string').encode('ascii', 'ignore')     

        # Add the new search to the database.
        new_search = UserSearch(user_id = this_user_id, 
                                search_string = search_string, 
                                user_default=is_default, 
                                timestamp = datetime.utcnow())
        db.session.add(new_search)
        db.session.commit()

    return jsonify({})

@app.route('/delete_search', methods=["POST"])
def delete_search():
    """
    This route responds to an AJAX request. It deletes a saved search from the database.

    Takes the user's ID and the search string they selected for deletion. 
    Returns nothing. Returns an empty JSON dictionary to prevent errors.
    """

    # Get the selected search string from the AJAX request.
    search_string = request.form.get('search_string').encode('ascii', 'ignore')
    this_user_id = session.get('user_id', None)

    print search_string

    # Parse the search string into a dictionary of parameters and values.
    param_list = search_string.split("&")
    search_to_delete = {param.split("=")[0]: param.split("=")[1] for param in param_list}

    # Get all of the user's searches
    user_searches = UserSearch.query.filter(UserSearch.user_id == this_user_id).all()

    # Parse each saved search string into a dictionary
    # Compare each dictionary to the dictionary of the selected search.
    # Upon finding a match, delete the matching search object.
    # This is necessary because two search strins may have the same parameters
    # But in a different order.
    for item in user_searches:
        item_params = item.search_string.split("&")
        search_dict = {param.split("=")[0]: param.split("=")[1] for param in item_params}
        if search_dict == search_to_delete:
            print "deleting:", search_dict
            itemid = item.search_id
            db.session.delete(item)
            db.session.commit()
            print db.session.query(UserSearch.search_string).filter(UserSearch.search_id == itemid).all()


    return jsonify({})

@app.route('/saved_searches', methods=["GET"])
def show_saved_searches():
    """
    Display the user's saved searches.

    This route queries the database directly.
    Returns a list of dictionaries.
    """
    # This will return None if the user is not logged in
    this_user_id = session.get('user_id', None)                               

    if this_user_id is not None:                                       
        # get a list of the user's searches from the DB
        search_list = db.session.query(UserSearch.search_string).filter(UserSearch.user_id == this_user_id).all()

        if search_list:
            print "found search list: ", search_list

        # Create a list of lists, splitting each search string on &
        param_list = [this_list.search_string.split("&") for this_list in search_list]
        for thislist in param_list:
            print thislist, len(thislist)
        
        # Create a list of dictionaries where list[n] = {search parameter: parameter value, ...}
        final_list = []
        if param_list is not []:
            for converted_list in param_list:               # Nested for loops FIXME
                if converted_list is not ['']:
                    print "True"
                    this_dict = {}
                    for item in converted_list:
                        this = item.split("=")
                        this_dict[this[0]] = this[1]
                    final_list.append(this_dict)
        else:
            print "The parameter list was empty."

        return render_template("saved_searches.html", search_list=final_list, SPUH_EQUIVALENTS=SPUH_EQUIVALENTS, REGION_CODES=REGION_CODES)
    else:
        flash('Please log in to access saved searches')
        return redirect('/')

@app.route('/change_default', methods=["POST"])
def change_default():
    """
    Set the user's default search.

    This route queries the database directly.
    Takes the user's id and a string that represents the new default search.
    """

    print "Setting a new user default search."

    this_user_id = session.get('user_id', None)

    if this_user_id is not None:
        # get the new default search string from the form
        new_default_string = request.form.get('search_string').encode('ascii', 'ignore')
        print "default called search string:",  new_default_string

        if new_default_string == '':
            print "Empty string"
        else:
            # see if this user already has a default set.
            user_default = UserSearch.query.filter(UserSearch.user_id == this_user_id,
                                           UserSearch.user_default == True).first()
            # If the user already has a default set, remove its is_default flag.
            if user_default:
                print "user default:", user_default.search_string
                user_default.user_default = 0
                db.session.commit()
            else:
                print "No preexisting user default found."

            # see if this user already has this search saved.
            preexisting_version = UserSearch.query.filter(UserSearch.user_id == this_user_id, 
                                                        UserSearch.search_string == new_default_string).first()
            if preexisting_version:
                print "found it!", preexisting_version.search_string            # parse these FIXME
                preexisting_version.user_default = 1
                db.session.commit()
            else:
                print "Adding a new copy of %s to the database" %new_default_string
                new_search = UserSearch(user_id = this_user_id, 
                                        search_string = new_default_string, 
                                        user_default=1, 
                                        timestamp = datetime.utcnow())
                db.session.add(new_search)
                db.session.commit()
        

    return jsonify({})
        

##############################################################################
# SIGNUP/LOGIN ROUTES

@app.route('/login')
def login():
    """
    Log in with Twitter.
    """

    print "in the Twitter login"
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    """
    Handle the response from the Twitter login.

    Sets session variables.
    This route queries the database directly.
    """

    # Twitter/oauth functions
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    # Add the user's Twitter information to their session.
    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    
    # Look for a user whose username matches the screen name from the Twitter response.
    user_object = User.query.filter(User.username == resp['screen_name']).first()

    # If no users matches, add this new user to the database.
    if user_object is None:
        new_user = User(username = resp['screen_name'])     # FIXME to ask the user for more information if it's their first time.
        db.session.add(new_user)
        db.session.commit()
        user_object = User.query.filter(User.username == resp['screen_name']).first()

    user_id_input = user_object.user_id

    # Add username and user id to the session.
    session['username'] = resp['screen_name']
    session['user_id']  = user_id_input
    print session

    flash('You were signed in as %s' % session['username'])
    return redirect(next_url)

@app.route('/signup', methods=["GET"])
def show_signup():
    """
    Render the signup page
    """

    return render_template("signup.html")

@app.route('/signup', methods=["POST"])
def process_signup():
    """
    Get the user's name, password, and email.
    Add them to the database
    Then send them to the homepage and make them log in.
    """

    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
                                            # FIXME to check for preexisting usernames
    new_user = User(username=username,      # create a User object
                    password=password,
                    email=email,
                    bird_count=0)
    db.session.add(new_user)                # add the new user to the database
    db.session.commit()
    flash('New account created! Please log in.')

    return redirect('/lek_login', code=307)

# OLD LOGIN ROUTES
@app.route('/lek_login', methods=["GET"])
def show_login():
    """
    Render the login page
    """

    return render_template("login.html")

@app.route('/lek_login', methods=["POST"])
def process_login():
    """
    Login form input. Checks the username and password against the database
    Then either sets the session variables or tells the user to try again
    """

    username_input = request.form.get("username")
    password_input = request.form.get("password")

    try: 
        user_object = User.query.filter(User.username == username_input, User.password == password_input).first()
        user_id_input = user_object.user_id
    except AttributeError:
        user_id_input = "guest"

    if user_id_input is "guest":
        flash('No such user found. Create a new account or log in.')
        return redirect('/login')

    else:
        session['username'] = username_input
        session['password'] = password_input
        session['user_id']  = user_id_input

        return redirect('/')

@app.route('/logout')
def logout():
    """
    Clear the user's session variable
    Render the homepage.
    """

    session.clear()
    flash('You have logged out.')
    return redirect('/')

##############################################################################
# OBSERVATION ROUTES
@app.route('/add_obs', methods=["POST"])
def add_obs():
    """
    This route responds to an AJAX request. Adds a new row to the observations table.

    This route queries the database directly.
    Does not return a view. Only returns victory.
    """
    
    # Get the user's id
    this_user_id = session.get('user_id', None)

    if this_user_id is not None:
        # Get the bird's ID from the AJAX request.
        bird_id = request.form.get('bird')

        # Query the database for an observation matching this user and this bird id.
        obs = Observation.query.filter(Observation.bird_id == bird_id, 
                                       Observation.user_id == this_user_id).first()

        # If the observation exists, delete it.
        # Otherwise, create a new observation.
        if obs:
            print "deleting", obs
            db.session.delete(obs)
            db.session.commit()
        else:
            print "wow new obs"
            print "user id and bird id", this_user_id, bird_id
            new_obs = Observation(  user_id = this_user_id,
                                    bird_id = bird_id,
                                    timestamp = datetime.utcnow() )
            db.session.add(new_obs)
            db.session.commit()


    return "Victory!"

##############################################################################
# MAP ROUTES
@app.route('/map')
def map():
    return render_template("maptemp.html")

##############################################################################
# Things to do when this app is run.
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    # Connect the Flask app defined at the top of the file
    # To the database defined in model.py
    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    # Run.
    app.run()