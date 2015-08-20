"""Lek website"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import json                                         # FIXME
import requests     # FIXME
from flask_oauth import OAuth
import os
import twitter

from datetime import datetime

from model import User, Bird, Observation, UserSearch, connect_to_db, db

from searchbirds import birdsearch

app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "TINAMOU"

app.jinja_env.undefined = StrictUndefined

api = twitter.Api(
    consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
    access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
print api.VerifyCredentials()

twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET']
)

# should probably move these variables to their own file.

# common names for bird orders
SPUH_EQUIVALENTS = {'Struthioniformes' : "Ostriches",
                    'Rheiformes' : "Rheas",
                    'Casuariiformes' : "Cassowaries and emus",
                    'Apterygiformes' : "Kiwis",
                    'Tinamiformes' : "Tinamous",
                    'Anseriformes' : "Ducks, geese, and swans",
                    'Galliformes' : "Pheasants, quail, megapodes, curassows",
                    'Gaviiformes' : "Loons and divers",
                    'Podicipediformes' : "Grebes",
                    'Phoenicopteriformes' : "Flamingos",
                    'Sphenisciformes' : "Penguins",
                    'Procellariiformes' : "Albatross",
                    'Phaethontiformes' : "Tropicbirds",
                    'Ciconiiformes' : "Storks",
                    'Suliformes' : "Frigatebirds, gannets, and darters",
                    'Pelecaniformes' : "Pelicans",
                    'Accipitriformes' : "Hawks, eagles, and vultures",
                    'Falconiformes' : "Falcons and caracaras",
                    'Otidiformes' : "Bustards",
                    'Mesitornithiformes' : "Mesites",
                    'Cariamiformes' : "Seriemas",
                    'Eurypygiformes' : "Kagus",
                    'Gruiformes' : "Cranes",
                    'Charadriiformes' : "Waders, gulls, and auks",
                    'Pterocliformes' : "Sandgrouse",
                    'Columbiformes' : "Pigeons and doves",
                    'Psittaciformes' : "Parrots",
                    'Musophagiformes' : "Turacos",
                    'Opisthocomiformes' : "Hoatzin",
                    'Cuculiformes' : "Cuckoos",
                    'Strigiformes' : "Owls",
                    'Caprimulgiformes' : "Nightjars, oilbirds, and potoos",
                    'Apodiformes' : "Swifts and hummingbirds",
                    'Coliiformes' : "Mousebirds",
                    'Trogoniformes' : "Trogons",
                    'Coraciiformes' : "Kingfishers, rollers, motmots, bee-eaters",
                    'Leptosomiformes' : "Cuckoo roller",
                    'Bucerotiformes' : "Hornbills and hoopoes",
                    'Piciformes' : "Woodpeckers",
                    'Passeriformes' : "Songbirds"}

# rationalizing location codes
REGION_CODES = {  "NA" : "North America",
                  "MA" : "Middle America",
                  "SA" : "South America",
                  "LA" : "Latin America",
                  "AF" : "Africa",
                  "EU" : "Eurasia",
                  "OR" : "South Asia",
                  "AU" : "Australasia",
                  "AO" : "Atlantic Ocean",
                  "PO" : "Pacific Ocean",
                  "IO" : "Indian Ocean",
                  "TrO": "Tropical Ocean",
                  "TO" : "Temperate Ocean",
                  "NO" : "Northern Ocean",
                  "SO" : "Southern Ocean",
                  "AN" : "Antarctica",
                  "So. Cone" : "Southern Cone"
}

# Housekeeping over. Now for routes.
##############################################################################
# HOMEPAGE ROUTES

@app.route('/')
def index():
    """
    Homepage.

    Displays a dynamic list of bird species organized by order and family
    """

    this_user_id = session.get('user_id')                               # if the user is logged in, this will return their ID

    user_default = None

    if this_user_id: # use the user's presets for birdsearch if they have any
        user_default = UserSearch.query.filter(UserSearch.user_id == this_user_id, 
                                                   UserSearch.user_default == True).first()
    if this_user_id and user_default:
        print "default?", user_default.search_string

        if user_default:
            print "found search list.", user_default

        param_list = user_default.search_string.split("&")

        search_dict = {}        # FIXME

        for item in param_list:
            this = item.split("=")
            search_dict[this[0]] = this[1]
        
        print search_dict

        bird_dict = birdsearch(this_user_id, 
                              search_dict["which_birds"], 
                              search_dict["select_spuh"], 
                              search_dict["select_order"], 
                              search_dict["select_family"], 
                              search_dict["select_region"])
    else:                                                               # otherwise, show the generic page
        bird_dict = birdsearch()

    return render_template("homepage.html", birds_nest=bird_dict["birds_dict"], orders=bird_dict["orders"])

@app.route('/bird_gallery')
def bird_gallery():

    bird_thumbnails = []

    this_user_id = 4          # FIXME

    # base_url = "http://www.arkive.org/api/KjJPGXLFF6CLL5FOvk_Lx8JRvSuBJH1R1tmoGXFrYcE1/portlet/latin/%s/1"

    if this_user_id is not None:
                                                                        # get a list of the user's observations from the DB
        bird_ids_list = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id).all()

        bird_ids = [bird_id[0].encode('ascii', 'ignore') for bird_id in bird_ids_list]

    return render_template("gallery.html", bird_ids=bird_ids)

@app.route('/bird_pictures')
def bird_pictures():

    base_url = "http://www.arkive.org/api/KjJPGXLFF6CLL5FOvk_Lx8JRvSuBJH1R1tmoGXFrYcE1/portlet/latin/%s/1"

    bird_request = request.args.get('bird_id').encode('ascii', 'ignore')
    print bird_request

    this_bird_id = bird_request.lstrip('photo_')
    print "bird ID:", this_bird_id, type(this_bird_id)
    
    obs_list = db.session.query(Bird.sci_name).filter(Bird.taxon_id == this_bird_id).first()

    bird_name = obs_list[0].encode('ascii', 'ignore')
    print "Bird name:", bird_name

    target_url = base_url %bird_name

    ark_response = requests.get(target_url)
    ark_status = ark_response.status_code

    if ark_status == 200:
        print "Arkive status 200!"
        ark_response_data = json.dumps({'id': bird_request, 'uri': json.loads(ark_response.text)['results'][0].encode('ascii', 'ignore')})
    else:
        print "no bird found."
        ark_response_data = json.dumps({'id': bird_request, 'uri': '<span></span>'}) #<img src="static/birdfill.gif"></img>

    return ark_response_data

@app.route('/mark_user_birds', methods=["GET"])
def mark_birds():
    """
    I talk to AJAX. I return a jsonified list of the birds that the user has seen. I do not have a view.
    """

    this_user_id = session.get('user_id')                               # This will return None if the user is not logged in

    if this_user_id is not None:
                                                                        # get a list of the user's observations from the DB
        obs_list = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id).all()

                                                                        # clean up one-item tuples
        obs_dict = {obs[0]: '' for obs in obs_list}

        obs_json = jsonify(obs_dict)                                    # make a json string for the AJAX call

        return obs_json

@app.route('/birdcount', methods=["GET"])
def birdcount():
    """
    If a logged-in user loads the home page, query the database for the total number of rows
    in the observation table with that user's ID on them.

    Return the number of rows as a string for AJAX
    """

    this_user_id = session.get('user_id')                               

    if this_user_id:
        count = Observation.query.filter_by(user_id = this_user_id).count()

        return str(count)
    else:
        return str(0)                                                                      # return a string for the AJAX call

##############################################################################
# SEARCH ROUTES

@app.route('/search', methods=["GET"])
def search():
    """
    Search form. I pass the SPUH dictionary, a list of orders, 
    a list of (family, order) tuples, a list of bird objects,
    and the REGIONS dictionary to the search template.
    """
    spuh = SPUH_EQUIVALENTS                                                 # get the SPUH dictionary

    bird_dict = birdsearch()                                                # ask birdsearch for a list of all birds

    regions = REGION_CODES                                                  # get the REGION dictionary

    return render_template("search.html", orders=bird_dict["orders"], birds_nest = bird_dict["birds_dict"], regions=regions, spuh=spuh)

@app.route('/search', methods=["POST"])
def search_results():
    """
    Search form input.

    Pass user input strings to birdsearch. Also pass the user's ID if the user is logged in.
    Use the results from birdsearch to rerender the homepage.
    """
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
    return render_template("homepage.html", birds_nest=bird_dict["birds_dict"], orders=bird_dict["orders"])

@app.route('/add_search', methods=["POST"])
def add_search():
    """
    This function should add new searches to the database.

    It should be called with an ajax request from the client.
    It doesn't have to return anything (but it could return a confirmation...?)
    """

    print "Add search is running!"

    search_string = request.form.get('search_string')

    print search_string, type(search_string)
    this_user_id = session.get('user_id', None)       # get the user's ID from session, or get None

    print "THIS USER ID:", this_user_id

    if this_user_id is not None:
        is_default = 0  # might be able to take this out?

        search_string = request.form.get('search_string').encode('ascii', 'ignore')     # get the stringified form from the ajax request

        new_search = UserSearch(user_id = this_user_id, 
                                search_string = search_string, 
                                user_default=is_default, 
                                timestamp = datetime.utcnow())
        db.session.add(new_search)
        db.session.commit()

    return jsonify({})

@app.route('/saved_searches', methods=["GET"])
def show_saved_searches():
    """
    I get the user's searches from the UserSearch database table and display them.
    """
    this_user_id = session.get('user_id', None)                               # This will return None if the user is not logged in

    if this_user_id is not None:                                        # get a list of the user's searches from the DB

        search_list = db.session.query(UserSearch.search_string).filter(UserSearch.user_id == this_user_id).all()

        if search_list:
            print "found search list.", search_list

        param_list = [this_list.search_string.split("&") for this_list in search_list]

        print "PARAM LIST:", param_list
        
        final_list =[]

        if param_list is not []:
            for converted_list in param_list:
                this_dict = {}
                for item in converted_list:
                    this = item.split("=")
                    this_dict[this[0]] = this[1]
                final_list.append(this_dict)
        else:
            print "wtf"

        return render_template("saved_searches.html", search_list=final_list, SPUH_EQUIVALENTS=SPUH_EQUIVALENTS, REGION_CODES=REGION_CODES)
    else:
        flash('Please log in to access saved searches')
        return redirect('/')

@app.route('/change_default', methods=["POST"])
def change_default():
    """
    I am called when the user checks the "make this my new default" tick box
    I change the value of the user_default field in the database to "true"
    """

    # if an old default exists, make it no longer a default
    # if the search string already exists, make it default
    # otherwise... what? create it? or call the add_search method? must avoid conflict here

    print "The user default route fired."

    this_user_id = session.get('user_id', None)                               # This will return None if the user is not logged in
    print "default called user id:", this_user_id

    if this_user_id is not None:
        # get the new default search string from the form
        new_default_string = request.form.get('search_string').encode('ascii', 'ignore')
        print "default called search string:",  new_default_string

        # see if this user already has a default set.
        user_default = UserSearch.query.filter(UserSearch.user_id == this_user_id,
                                       UserSearch.user_default == True).first()

        if user_default:
            print "user default:", user_default.search_string
            user_default.user_default = 0
            db.session.commit()
        else:
            print "no user default."


        # see if this user already has this search saved.
        preexisting_version = UserSearch.query.filter(UserSearch.user_id == this_user_id, 
                                                    UserSearch.search_string == new_default_string).first()
        if preexisting_version:
            print "found it!", preexisting_version.search_string
            preexisting_version.user_default = 1
            db.session.commit()
        else:
            print "Apparently you called 'default' without calling 'save', wtf."
            print "Adding a new copy of %s to the database" %new_default_string
            new_search = UserSearch(user_id = this_user_id, 
                                    search_string = new_default_string, 
                                    user_default=1, 
                                    timestamp = datetime.utcnow())
            db.session.add(new_search)
            db.session.commit()



    #     print "search string", json.loads(search_string)

    #     if user_default is not None:
    #         print "old default", user_default.search_string
    #     else:
    #         print "No existing default."
        

    return None
        

##############################################################################
# SIGNUP/LOGIN ROUTES

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

    return redirect('/')

@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

# OLD LOGIN ROUTES
# @app.route('/login', methods=["GET"])
# def show_login():
#     """
#     Render the login page
#     """

#     return render_template("login.html") # but I want to put this in a modal window!

# @app.route('/login', methods=["POST"])
# def process_login():
#     """
#     Login form input. Checks the username and password against the database
#     Then either sets the session variables or tells the user to try again
#     """

#     username_input = request.form.get("username")
#     password_input = request.form.get("password")

#     try: 
#         user_object = User.query.filter(User.username == username_input, User.password == password_input).first()
#         user_id_input = user_object.user_id
#     except AttributeError:
#         user_id_input = "guest"

#     if user_id_input is "guest":
#         flash('No such user found. Create a new account or log in.')
#         return redirect('/login')

#     else:
#         session['username'] = username_input
#         session['password'] = password_input
#         session['user_id']  = user_id_input

#         return redirect('/')

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
    I talk to AJAX. I update the Observation table when users click on species names.

    I get the bird ID from AJAX and the user ID from session.

    I do not return a view. I return victory.
    """
    
    this_user_id = session.get('user_id')

    if this_user_id:
        bird_id = request.form.get('bird')

        obs = Observation.query.filter(Observation.bird_id == bird_id, 
                                       Observation.user_id == this_user_id).first()

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
# Stuff I didn't write that makes the app go.
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()