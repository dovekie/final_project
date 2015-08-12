"""Utility file to create the bird taxa database"""

from model import Bird, connect_to_db, db
import json
from server import app
import requests

def load_birds():
    """
    Load bird species data from eBird and Faircloth APIs into database.

    """
    # These two lines get the full ebird json. commented out for testing purposes.
    # ebird_response = requests.get("http://ebird.org/ws1.1/ref/taxa/ebird?cat=species&fmt=json&locale=en_US")
    # json_birds = ebird_response.json()

    bird_string = open("tests/ebird_complete.json").read() # these two lines are fake ebird input for testing
    json_birds = json.loads(bird_string)

    ebirds = {}

    for bird in json_birds:  # make a dict with the format: ebird[scientific name] = (taxonID, common name)
        bird_id = bird["taxonID"]
        common_name = bird["comName"]
        binom = bird["sciName"]
        ebirds[binom] = (bird_id, common_name)

    # These two lines get the full faircloth json. commented out for testing purposes.
    # faircloth_response = requests.get("http://birds.faircloth-lab.org/api/v1/species/?offset=0&limit=20000")
    # faircloth_birds = faircloth_response.json()

    faircloth_string = open("tests/faircloth_complete.json").read() # similar to above; fake faircloth input for testing
    faircloth_data = json.loads(faircloth_string)
    faircloth_birds = faircloth_data["records"]


    # match the faircloth data to the ebird data, and use both to create a new row in the birds table.
    # might be a good idea to convert this to ascii (it's unicode right now)
    # at the moment, ascii conversion is handled by server.py in /search GET route
    for bird in faircloth_birds:
        if bird["binomial"] in ebirds:
            binomial = bird["binomial"]

            new_bird = Bird(taxon_id = ebirds[binomial][0],
                            common_name = ebirds[binomial][1],
                            sci_name = bird["binomial"],
                            species = bird["species"],
                            genus = bird["genus"],
                            family = bird["family"],
                            order = bird["order"].title(),
                            region = bird["breed_region"],
                            subregion = bird["breed_subregion"],
                            nonbreeding_region = bird["nonbreed"]
                            )
            db.session.add(new_bird)
    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)  

    load_birds()

# Don't run this without running python -i model.py and doing db.create_all() first