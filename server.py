"""BirdGrip Website"""
"""("grip" is birder slang for bragging about one's sightings)"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Bird, Observation, connect_to_db, db

app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "TINAMOU"

app.jinja_env.undefined = StrictUndefined

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
REGION_CODES = { "NA" : "North America",
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

@app.route('/')
def index():
    """
    Homepage.

    Displays a dynamic list of bird species organized by order and family
    """

    # get all orders
    orders = db.session.query(Bird.order).order_by(Bird.taxon_id).group_by(Bird.order).all()

    # cleaning up the one-item tuples.
    orders_list = [order[0] for order in orders]
    
    # get all families, and all orders for all families
    families = db.session.query(Bird.family, Bird.order).order_by(Bird.taxon_id).group_by(Bird.family).all()

    # get all bird objects
    birds = Bird.query.order_by(Bird.taxon_id).all()

    return render_template("homepage.html", orders=orders_list, families = families, birds=birds)

@app.route('/mark_user_birds', methods=["GET"])
def mark_birds():
    
    # This will return None if the user is not logged in
    this_user_id = session.get('user_id')

    if this_user_id is not None:
        print this_user_id

        obs_list = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id).all()
        print len(obs_list)
        #clean up one-item tuples
        obs_dict = {obs[0]: '' for obs in obs_list}
        print obs_dict
        obs_json = jsonify(obs_dict)
        print obs_json

        return obs_json
    else:
        return {}  # FIXME

@app.route('/search', methods=["GET"])
def search():
    """
    Search form

    Get search parameter from the user
    """
    spuh = SPUH_EQUIVALENTS
    orders = Bird.query.order_by(Bird.taxon_id).group_by(Bird.order).all()
    families = Bird.query.order_by(Bird.taxon_id).group_by(Bird.family).all()
    regions = REGION_CODES

    return render_template("search.html", orders=orders, families=families, regions=regions, spuh=spuh)

@app.route('/search', methods=["POST"])
def search_results():
    """
    Search functions

    Take search parameters from the user and queries the database
    """
    bird_limit_param = request.form.get("which_birds")
    spuh_param = request.form.get("select_spuh")
    order_param = request.form.get("select_order")
    family_param = request.form.get("select_family")
    region_param = request.form.get("select_region")
    other_param = request.form.get("fuzzy")

    q = Bird.query

# Bird.query.filter(Bird.taxon_id.in_(list of bird ids))

    if bird_limit_param:
        this_user_id = session.get('user_id')
        obs_query = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id)
        obs_list = [obs[0] for obs in obs_query.all()]
        print "user = ", this_user_id
        print "query = ", obs_query
        print "and all = ", obs_query.all()
        print obs_list

        if bird_limit_param == "all_birds":
            pass

        elif bird_limit_param == "my_birds":
            pass
            # only show birds I have observed
            q = q.filter(Bird.taxon_id.in_(obs_list))

        elif bird_limit_param == "not_my_birds":
            pass
            # only show birds I have not observed
            q = q.filter(~Bird.taxon_id.in_(obs_list))

        # right now, "spuh" is just another way of picking an order
    if spuh_param:
        print "spuh: ", spuh_param, type(spuh_param)
        order_param = spuh_param

        # filter the query by order, if the user has selected an order parameter
    if order_param: 
        print "order ", order_param, type(order_param)
        q = q.filter_by(order = order_param)

    if family_param:
        q = q.filter_by(family = family_param)

        # search inside the region field
    if region_param:
        q = q.filter(Bird.region.like('%'+region_param+'%'))

    # put the final query in order by taxon ID
    q = q.order_by(Bird.taxon_id)

    # get a list of bird objects
    birds = q.all()

    # get a list of order objects
    orders_objects = q.group_by(Bird.order).all()

    # generate a list of orders
    orders_list = []
    for order in orders_objects:
        orders_list.append(order.order)

    # get a list of family objects
    families_objects = q.group_by(Bird.family).all()

    # generate a list of (family, order) tuples
    families = []
    for family in families_objects:
        families.append((family.family, family.order))

    return render_template("homepage.html", orders=orders_list, families = families, birds=birds)


# def searchfunct(list (maybe a dictionary?) of arguments):
    # actually a dictionary might not be a bad idea; could be searchdict["parameter"] = "paramater value"

    #anyway

    # use the parameters to filter the complete species list
    # then do the grouping by order and family!
    # that way: no empty orders/families
    # the default needs to return all species
    # this function could return species, family, order
    # or just return the species list and let the routes fight it out

@app.route('/signup', methods=["GET"])
def show_signup():
    return render_template("signup.html")

@app.route('/signup', methods=["POST"])
def process_signup():

    username = request.form.get("username").lower()
    password = request.form.get("password")
    email = request.form.get("email")

    new_user = User(username=username,
                    password=password,
                    email=email,
                    bird_count=0)
    db.session.add(new_user)
    db.session.commit()
    flash('New account created! Please log in.')

    return redirect('/')

@app.route('/login', methods=["GET"])
def show_login():
    return render_template("login.html") # but I want to put this in a modal window!

@app.route('/login', methods=["POST"])
def process_login():

    username_input = request.form.get("username")
    password_input = request.form.get("password")
    user_object = User.query.filter(User.username == username_input, User.password == password_input).first()
    user_id_input = user_object.user_id
    bird_count_input = user_object.bird_count

    session['username'] = username_input
    session['password'] = password_input
    session['user_id']  = user_id_input

    return redirect('/')

@app.route('/logout')
def logout():
    """
    Clear the user's session variable
    """

    session.clear()

    return redirect('/')


@app.route('/add_obs', methods=["POST"])
def add_obs():
    
    try:
        this_user = session['username']
    except KeyError:
        this_user = "guest"

    print "this username:", this_user

    if this_user is not "guest":
        user_id = User.query.filter(User.username == session['username']).one().user_id

        print "this user_id", user_id
        
        count = request.form.get('count')
        bird_id = request.form.get('bird')

        obs = Observation.query.filter(Observation.bird_id == bird_id, Observation.user_id == user_id).first()

        if obs:
            print "deleting", obs
            db.session.delete(obs)
            db.session.commit()
        else:
            print "wow new obs"
            print "user id and bird id", user_id, bird_id
            new_obs = Observation(  user_id = user_id,
                                    bird_id = bird_id,
                                    timestamp = "0")
            db.session.add(new_obs)
            db.session.commit()


    return "Victory"

# Stuff I didn't write that makes the app go.
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()