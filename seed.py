"""Utility file to create the bird taxa database"""

from model import Bird, connect_to_db, db
import json
from server import app
import requests

def load_birds():
    """Load bird species data from eBird into database.

    """
    # This part gets the full ebird json. commented out for testing purposes.
    # ebird_response = requests.get("http://ebird.org/ws1.1/ref/taxa/ebird?cat=species&fmt=json&locale=en_US")

    # json_birds = ebird_response.json()

    bird_string = open("tests/bird_data_sample_expanded.txt").read()

    json_birds = json.loads(bird_string)

    for bird in json_birds:
        bird_id = bird["taxonID"]
        binom = bird["sciName"]     # get the bird's binomial from eBird

        faircloth_url = "http://birds.faircloth-lab.org/api/v1/species/scientific/" + binom         # build a url for querying Faircloth's API
        faircloth_request = requests.get(faircloth_url)         # the raw response object from Faircloth
        bird_json = faircloth_request.json()        # JSON data out of the request object
        bird_records = bird_json["records"][0]      # just the good stuff. Dict key "records" has a list as a value. Get the first item in the list.

        #done processing. Now to get data!
        species = bird_records["species"]
        genus = bird_records["genus"]
        family = bird_records["family"]
        order = bird_records["order"].title() # dunno why this is uppercase. Fixing that...
        region = bird_records["breed_region"]
        subregion = bird_records["breed_subregion"]
        nonbreeding = bird_records["nonbreed"]

        bird = Bird(taxon_id = bird["taxonID"],
                    common_name = bird["comName"],
                    sci_name = bird["sciName"],
                    species = bird_records["species"],
                    genus = bird_records["genus"],
                    family = bird_records["family"],
                    order = bird_records["order"].title(),
                    region = bird_records["breed_region"],
                    subregion = bird_records["breed_subregion"],
                    nonbreeding_region = bird_records["nonbreed"]
                    )
        db.session.add(bird)

    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)  

    load_birds()

# Don't run this without running python -i model.py and doing db.create_all() first