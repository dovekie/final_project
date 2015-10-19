from model import User, Bird, Observation, connect_to_db, db
import pprint

def birdsearch(this_user_id = None, bird_limit = "all", spuh = "all", order="all", family = "all", region = "all", other=None):
	""" 
	I take parameters from the server and return a list of orders and a dictionary like so:
	dict = {order: {family_1: {birdA: {bird: data}, birdB: {bird: data}}}}
	"""
	
	def test_for_semicolons(term):
		"""
		Take a str and look for any semicolons.

		Returns True if no semicolons are found (true = probably not malicious input)
		"""

		if term.find(';') == -1:
			return True
		else:
			return False

	semicolon_test_results = map(test_for_semicolons, locals().keys())

	if False in semicolon_test_results:
		return "Semicolons are not allowed in birdsearch inputs."


	# begin building an SQL query
	q = Bird.query
	print "Running query"

	# If the user is filtering by whether or not a bird is on their life list
	if bird_limit != "all":
		print "bird limit var: ", bird_limit  
		print "user id: ", this_user_id 
		obs_query = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id)
		obs_list = [obs[0] for obs in obs_query.all()]

		# Only show birds the user HAS seen.
		if bird_limit == "my_birds": # this will be called with "my_birds" whenever a logged in user loads the homepage.
			q = q.filter(Bird.taxon_id.in_(obs_list))

		# only show birds the user HAS NOT seen.
		elif bird_limit == "not_my_birds":
			q = q.filter(~Bird.taxon_id.in_(obs_list))

	# right now, "spuh" is just another way of picking an order
	if spuh != "all":
		print "spuh: ", spuh, type(spuh)
		order = spuh

	if order !="all": 
		print "order ", order, type(order)
		q = q.filter_by(order = order)

	if family != "all":
		q = q.filter_by(family = family)

    # search inside the region field
	if region != "all":
		print "region ", region
		q = q.filter(Bird.region.like('%'+region+'%'))

    # put the final query in order by taxon ID
	q = q.order_by(Bird.taxon_id)

	##### Now the query that has been built is run several times.

	# Run once to get a list of bird objects
	birds = q.all()

	# Run once to get a list of family objects
	families_objects = q.group_by(Bird.family).all()

	# Run once to get a list of order objects
	orders_objects = q.group_by(Bird.order).all()

	# generate a list of orders as ascii strings.
	orders_list = [order.order.encode('ascii', 'ignore') for order in orders_objects]

	# begin the big dictionary of birds with the orders (strings) as keys.
	birds_dict = {order: {} for order in orders_list}

	# add families as ascii strings to the big dictionary of birds
	for family in families_objects:
		birds_dict[family.order.encode('ascii', 'ignore')][family.family.encode('ascii', 'ignore')] = {}

	# add birds to the big dictionary of birds.
	# Pull relevant data out of each bird object.
	for bird in birds:
		birds_dict[bird.order.encode('ascii', 'ignore')][bird.family.encode('ascii', 'ignore')][bird.taxon_id.encode('ascii', 'ignore')] = {'order': bird.order.encode('ascii', 'ignore'), 
																												  'family': bird.family.encode('ascii', 'ignore'), 
																												  'sci_name': bird.sci_name, 
																												  'common_name': bird.common_name,
																												  'region': bird.region}

	# FOR FUTURE REFERENCE:
	# for order in orders_list:
	# 	for family in birds_dict[order].keys():
	# 		print ">>>", family
	# 		for bird in birds_dict[order][family].keys():
	# 			print ">>> >>>", bird

	return {"birds_dict": birds_dict,
			"orders" : orders_list}
