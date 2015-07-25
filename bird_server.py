import json
import requests
from datetime import datetime
import time
# import model

def get_birds():


	# Gets a current list of bird taxa from Cornell's eBird API
	locale_code = "en_US"
	r = requests.get("http://ebird.org/ws1.1/ref/taxa/ebird?cat=species&fmt=json&locale=" + locale_code)
	bird_raw_list = r.json()

	bird_dict = {}

	for bird_raw_dict in bird_raw_list:

		bird_dict[bird_raw_dict["taxonID"]] = [bird_raw_dict["sciName"], bird_raw_dict["comName"]]

	print bird_dict["TC000017"]


get_birds()

	#print r

	# one bird looks like this
	# {"bandingCodes":[],
	# 	"category":"species",
	#	"comName":"Ostrich",
	#	"comNameCodes":["SOOS","COOS","OSTR"],
	#	"sciName":"Struthio camelus",
	#	"sciNameCodes":["STCA"],
	#	"speciesCode":"ostric1",
	#	"taxonID":"TC000001",
	#	"taxonOrder":1
	#  }

	# for feature in r.json()['features']:
	# 	# print "************************"
	# 	# print feature['geometry']['coordinates'][1]
		
	# 	new_quake = model.Quake(
	# 		quake_id = feature['id'], 
	# 		quake_title = feature['properties']['title'],
	# 		quake_type = feature['properties']['type'],
	# 		magnitude = feature['properties']['mag'],
	# 		place = feature['properties']['place'],
	# 		latitude = feature['geometry']['coordinates'][0],
	# 		longitude = feature['geometry']['coordinates'][1],
	# 		depth = feature['geometry']['coordinates'][2],
	# 		quake_datetime = datetime.fromtimestamp(feature['properties']['time']/1000),
	# 		url = feature['properties']['url'],
	# 		seismictype = feature['properties']['type'],
	# 		status = feature['properties']['status'],
	# 		felt = feature['properties']['felt'],
	# 		tsunami = feature['properties']['tsunami'],
	# 		recordtime = datetime.now())

	# 	# print "**************************"
	# 	# print new_quake

	# 	model.session.merge(new_bird)
	# 	#use merge if the data can change and be update
	# 	#use add if the data is fairly static
	# 	model.session.commit()





# if __name__ == '__main__':
# 	get_birds()