from model import User, Bird, Observation, connect_to_db, db

def birdsearch(this_user_id = None, bird_limit = "all", spuh = "all", order="all", family = "all", region = "all", other=None):
	""" I take parameters from the server and return lists, lists of tuples, and lists of objects"""

	q = Bird.query

	if bird_limit is not "all":
		print "bird limit var: ", bird_limit
		print "user id: ", this_user_id
		obs_query = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id)
		obs_list = [obs[0] for obs in obs_query.all()]

		# print "obslist", obs_list

		if bird_limit == "my_birds":
		# only show birds I have observed
			q = q.filter(Bird.taxon_id.in_(obs_list))

		elif bird_limit == "not_my_birds":
		# only show birds I have not observed
			q = q.filter(~Bird.taxon_id.in_(obs_list))


	# right now, "spuh" is just another way of picking an order
	if spuh != "all":
		# print "spuh: ", spuh, type(spuh)
		order = spuh
		# print "first spuh: ", q.first()

	if order !="all": 
		# print "order ", order, type(order)
		q = q.filter_by(order = order)
		# print "first order ", q.first()


	if family != "all":
		q = q.filter_by(family = family)
		# print "first family", q.first()

        # search inside the region field
	if region != "all":
		q = q.filter(Bird.region.like('%'+region+'%'))
		print "ALL THE REGIONS ", q.all()

    # put the final query in order by taxon ID
	q = q.order_by(Bird.taxon_id)

	# get a list of bird objects
	birds = q.all()
	# print "birds? ", type(birds), 
	# try:
	# 	print birds[0]
	# except IndexError:
	# 	print "no birds."

	# get a list of order objects
	orders_objects = q.group_by(Bird.order).all()

	# generate a list of orders
	orders_list = []
	for order in orders_objects:
		unicode_order = order.order
		ascii_order = unicode_order.encode('ascii', 'ignore')
		orders_list.append(order.order)

	# get a list of family objects
	families_objects = q.group_by(Bird.family).all()

	# generate a list of (family, order) tuples
	families = []
	for family in families_objects:
		unicode_order = family.order
		unicode_family = family.family
		ascii_order = unicode_order.encode('ascii', 'ignore')
		ascii_family = unicode_family.encode('ascii', 'ignore')
		families.append((family.family, ascii_order))

	return {"orders" : orders_list,
			"families": families,
			"birds" : birds}
