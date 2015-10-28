from model import User, Bird, Observation, connect_to_db, db
#import pprint

def birdsearch(this_user_id = None, bird_limit = "all", spuh = "all", order="all", family = "all", region = "all", other=None, display_limit=50, offset=None):
	""" 
	I take parameters from the server and return a list of orders and a dictionary like so:
	dict = {order: {family_1: {birdA: {bird: data}, birdB: {bird: data}}}}
	"""
	print "birdsearch is go!"
	q = Bird.query
	# print "birdquery is go!"

	if bird_limit != "all":
		print "bird limit var: ", bird_limit  
		print "user id: ", this_user_id 
		obs_query = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id)
		obs_list = [obs[0] for obs in obs_query.all()]

		# print "obslist", obs_list

		if bird_limit == "my_birds": # this will be called with "my_birds" whenever a logged in user loads the homepage. Chill.
		# only show birds I have observed
			q = q.filter(Bird.taxon_id.in_(obs_list))

		elif bird_limit == "not_my_birds":
		# only show birds I have not observed
			q = q.filter(~Bird.taxon_id.in_(obs_list))


	# right now, "spuh" is just another way of picking an order
	if spuh != "all":
		print "spuh: ", spuh, type(spuh)
		order = spuh
		# print "first spuh: ", q.first()

	if order !="all": 
		print "order ", order, type(order)
		q = q.filter_by(order = order)
		# print "first order ", q.first()


	if family != "all":
		q = q.filter_by(family = family)
		# print "first family", q.first()

        # search inside the region field
	if region != "all":
		print "region ", region
		q = q.filter(Bird.region.like('%'+region+'%'))

    # put the final query in order by taxon ID
	q = q.order_by(Bird.taxon_id)

	# get a list of bird objects
	birds = q.limit(display_limit).all()

	all_taxons = [{bird.taxon_id: {'order': bird.order.encode('ascii', 'ignore'), 
								   'family': bird.family.encode('ascii', 'ignore'), 
								   'sci_name': bird.sci_name, 'common_name': bird.common_name, 
								   'region': bird.region}} 
				  for bird in birds]

	birds_dict = {}

	for bird in birds:
		this_order = birds_dict.get(bird.order)
		if this_order is None:
			print "adding order %s" %bird.order
			birds_dict[bird.order] = {bird.family: {bird.taxon_id: {'order': bird.order.encode('ascii', 'ignore'), 
																   'family': bird.family.encode('ascii', 'ignore'), 
																   'sci_name': bird.sci_name, 'common_name': bird.common_name, 
																   'region': bird.region}}}
		else:
			this_family = birds_dict[bird.order].get(bird.family)
			if this_family is None:
				print "adding family %s" %bird.family
				birds_dict[bird.order][bird.family] = {bird.taxon_id: {'order': bird.order.encode('ascii', 'ignore'), 
																	  'family': bird.family.encode('ascii', 'ignore'), 
																	  'sci_name': bird.sci_name, 'common_name': bird.common_name, 
																	  'region': bird.region}}
			else:
				birds_dict[bird.order][bird.family][bird.taxon_id] = {'order': bird.order.encode('ascii', 'ignore'), 
																     'family': bird.family.encode('ascii', 'ignore'), 
																     'sci_name': bird.sci_name, 'common_name': bird.common_name, 
																     'region': bird.region}

	# # get a list of family objects
	# families_objects = q.group_by(Bird.family).all()

	# get a list of order objects
	orders_objects = q.group_by(Bird.order).all()

	# generate a list of orders
	orders_list = [order.order.encode('ascii', 'ignore') for order in orders_objects]

	# # begin the big dictionary of birds
	# birds_dict = {order: {} for order in orders_list}

	# # add families to the big dictionary of birds
	# for family in families_objects:
	# 	birds_dict[family.order.encode('ascii', 'ignore')][family.family.encode('ascii', 'ignore')] = {}

	# #add birds to the big dictionary of birds
	# for bird in birds:
	# 	birds_dict[bird.order.encode('ascii', 'ignore')][bird.family.encode('ascii', 'ignore')][bird.taxon_id.encode('ascii', 'ignore')] = {'order': bird.order.encode('ascii', 'ignore'), 
	# 																											  'family': bird.family.encode('ascii', 'ignore'), 
	# 																											  'sci_name': bird.sci_name, 
	# 																											  'common_name': bird.common_name,
	# 																											  'region': bird.region}

	# FOR FUTURE REFERENCE:
	# for order in orders_list:
	# 	for family in birds_dict[order].keys():
	# 		print ">>>", family
	# 		for bird in birds_dict[order][family].keys():
	# 			print ">>> >>>", bird

	return {"birds_dict": birds_dict,
			"orders" : orders_list,
			"all_taxons": all_taxons}
