"""BirdGrip Website"""
"""("grip" is birder slang for bragging about one's sightings)"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Bird, Observation, connect_to_db, db

app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "TINAMOU"

app.jinja_env.undefined = StrictUndefined

# Housekeeping over. Now for routes.
SPUH_EQUIVALENTS = {'Struthioniformes' : "Ostriches",
                    'Rheiformes' : "Rheas",
                    'Casuariiformes' : "Cassowaries",
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

@app.route('/')
def index():
    """
    Homepage.

    Displays a dynamic list of bird species organized by order and family
    """

    orders = Bird.query.order_by(Bird.taxon_id).group_by(Bird.order).all()
    families = Bird.query.order_by(Bird.taxon_id).group_by(Bird.family).all()
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



    return render_template("homepage.html", orders=orders, families = families, birds=birds)

@app.route('/search', methods=["GET"])
def search():
    """
    Search form

    Get search parameter from the user
    """
    spuh = SPUH_EQUIVALENTS
    orders = Bird.query.order_by(Bird.taxon_id).group_by(Bird.order).all()
    families = Bird.query.order_by(Bird.taxon_id).group_by(Bird.family).all()
    regions = Bird.query.order_by(Bird.taxon_id).group_by(Bird.region).all()

    return render_template("search.html", orders=orders, families=families, regions=regions, spuh=spuh)

@app.route('/search', methods=["POST"])
def search_results():
    """
    Search functions

    Take search parameters from the user and queries the database
    """
    spuh_param = request.form.get("select_spuh")
    order_param = request.form.get("select_order")
    family_param = request.form.get("select_family")
    region_param = request.form.get("select_region")

    if spuh_param:
        order_param = spuh_param

    if order_param:
        print order_param, type(order_param)
        raw_orders = Bird.query.order_by(Bird.taxon_id).filter(Bird.order == order_param)
        orders = raw_orders.group_by(Bird.order).all()
    else:
        orders = Bird.query.order_by(Bird.taxon_id).group_by(Bird.order).all()
    
    if family_param:
        print family_param, type(family_param)
        raw_families = Bird.query.order_by(Bird.taxon_id).filter(Bird.family == family_param)
        families = raw_families.group_by(Bird.family).all()
    else:
        families = Bird.query.order_by(Bird.taxon_id).group_by(Bird.family).all()

    if region_param:
        print region_param, type(region_param)
        birds = Bird.query.order_by(Bird.taxon_id).filter(Bird.region==region_param).all()
    else:
        birds = Bird.query.order_by(Bird.taxon_id).all()

    return render_template("homepage.html", orders=orders, families = families, birds=birds)


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

    username = request.form.get("username")
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
    bird_count_input = user_object.bird_count

    session['username'] = username_input
    session['password'] = password_input

    return redirect('/')

@app.route('/logout')
def logout():
    """
    Clear the user's session variable
    """

    session.clear()

    return redirect('/')



# Stuff I didn't write that makes the app go.
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()