"""Lek website"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import json                                         # FIXME

from datetime import datetime

from model import User, Bird, Observation, UserSearch, connect_to_db, db

from searchbirds import birdsearch

app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "TINAMOU"

app.jinja_env.undefined = StrictUndefined

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

        default_string = user_default.search_string

        default_dict = json.loads(default_string)

        for key, value in default_dict.iteritems():
            print key, value[0]

        spuh = default_dict['select_spuh'][0]
        order = default_dict['select_order'][0]
        family = default_dict['select_family'][0]
        region = default_dict['select_region'][0]
        bird_limit = default_dict['which_birds'][0]

        session["default_view"] = default_string


        bird_dict = birdsearch(this_user_id, bird_limit, spuh, order, family, region)
    else:                                                               # otherwise, show the generic page
        bird_dict = birdsearch()

    return render_template("homepage.html", orders=bird_dict["orders"], families = bird_dict["families"], birds=bird_dict["birds"])

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
    If a logged-in user loads the home page, call birdsearch with the user's ID and "my_birds"
    """

    this_user_id = session.get('user_id')                               

    if this_user_id:
        birds_dict = birdsearch(this_user_id = this_user_id, bird_limit = "my_birds")       # ask birdsearch for all the birds seen by a user
        count = len(birds_dict["birds"])                                                    # get the length of the list of bird objects

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

    return render_template("search.html", orders=bird_dict["orders"], families = bird_dict["families"], regions=regions, spuh=spuh)

@app.route('/search', methods=["POST"])
def search_results():
    """
    Search form input.

    Pass user input strings to birdsearch. Also pass the user's ID if the user is logged in.
    Use the results from birdsearch to rerender the homepage.
    """
    # get the user's id
    this_user_id = session.get('user_id')

    # get the user's search request as a json string
    search_response = dict(request.form)  # get the entire request object and turn it into a dictionary
    search_storage_string = json.dumps(search_response) # turn the dict into a json string

    print "Search string: ", search_storage_string, type(search_storage_string) # leaving this for diagnostics

    # if the user wants to save their search
    search_param = request.form.get("save_this", None)
    default_param = request.form.get("set_default", None)

    if default_param:
        set_default = 1
    else:
        set_default = 0

    if search_param == "true":  # if the user wants to save a search
        print "So you want to save a search?", search_param
        print "Saving new search: ", search_storage_string
        new_search = UserSearch(user_id = this_user_id, 
                                search_string = search_storage_string, 
                                user_default=set_default, 
                                timestamp = datetime.utcnow())
        db.session.add(new_search)
        db.session.commit()

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
    return render_template("homepage.html", orders=bird_dict["orders"], families = bird_dict["families"], birds=bird_dict["birds"])

@app.route('/saved_searches', methods=["GET"])
def show_saved_searches():
    """
    I get the user's searches from the UserSearch database table and display them.
    """
    this_user_id = session.get('user_id')                               # This will return None if the user is not logged in

    if this_user_id is not None:
                                                                        # get a list of the user's searches from the DB

        search_list = db.session.query(UserSearch.search_string, UserSearch.timestamp).filter(UserSearch.user_id == this_user_id).all()

        search_list = [json.loads(this_search[0]) for this_search in search_list]
        print search_list

        return render_template("saved_searches.html", search_list=search_list, SPUH_EQUIVALENTS=SPUH_EQUIVALENTS, REGION_CODES=REGION_CODES)
    else:
        flash('Please log in to access saved searches')
        return redirect('/')
        

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

@app.route('/login', methods=["GET"])
def show_login():
    """
    Render the login page
    """

    return render_template("login.html") # but I want to put this in a modal window!

@app.route('/login', methods=["POST"])
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