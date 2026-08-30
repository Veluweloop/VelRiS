from asyncio import timeout
from cmath import isnan
from datetime import datetime
from os import system
import threading
import csv
import time
import requests
import pymysql.cursors
import json

# op termijn verwijderen
import config #import the config of the app

# hier staan de externe tools welke worden geimporteerd. Helper scripts zijn ondersteunend en de webbapp is the flask server
import webapp.webapp #local webserver for entering manual data
import helper_database #import the database_init of the app
import helper_api #import helpder function for api interaction with external servers

event_trigger = threading.Event() #create event trigger for background tasks

def on_boot():
#    print('boot')
    helper_database.create_tables() # build database if it doesnt exist yet
    update_background() #load all data from the server and insert it in the database

# ik heb hier een loop nodig die de data opvraagd vanuit de api en het wegschrijft in de database
# de background updates gaan schedulen op basis van een cronjob
# ik mis de optie voor het uploaden van de doorkomsten die niet gelukt zijn bij de eerste poging, en het downloaden van nieuwe data van de server
# toevoegen van try statements om te voorkomen dat de hele loop stopt bij een fout
def update_background():

    # loading all events and placing them in the database
#    EVENEMENT_json = helper_api.load_events(api=helper_database.get_instelling('API_events'))
#    for evenementen in EVENEMENT_json:
#        helper_database.insert_evenement(evenementen["EVENEMENT_ID"], 
#                                         evenementen["EVENEMENT_NAAM"])

    # loading competition info from the server and inserting it in the database
    competitioninfo = helper_api.load_competitioninfo(
        EVENEMENT_ID= helper_database.get_instelling('EVENEMENT_ID'),
        api=helper_database.get_instelling('API_competitioninfo'),
        api_key=helper_database.get_instelling('API_KEY'))

    for route in competitioninfo["etappe_routes"]:
        helper_database.insert_wisselpunt(
            wisselpunt_id = route["ETAPPE_ID"],
            wisselpunt_naam = route["LOCATIE_NAAM_FINISH"],
            etappe_volgnummer = route["ETAPPE_VOLGNUMMER"],
            evenement_id = route["EVENEMENT_ID"]
        )
    for ploeg in competitioninfo["ploeglijst"]:
        helper_database.insert_ploeg(
            ploeg["PLOEG_ID"],
            ploeg["PLOEGNUMMER"],
            ploeg["PLOEGNAAM"],
            ploeg["EVENEMENT_ID"]
        )
    # update_live_doorkomsten() #update all doorkomsten which are not yet synced with the server

# update status on succes
def update_live_doorkomsten():
    doorkomsten_local = helper_database.get_doorkomsten()
    for doorkomst in doorkomsten_local:
        try:
            if doorkomst["STATUS"] == "NOSYNC":
                print(doorkomst)
                reponse = helper_api.insert_doorkomst(
                    EVENEMENT_ID = doorkomst["EVENEMENT_ID"],
                    etappeVolgnummer = doorkomst["ETAPPE_VOLGNUMMER"],
                    ploegNummer = doorkomst["PLOEG"],
                    doorkomstTijd = doorkomst["DATETIME"],
                    api = "https://veluweloop.nl/api/doorkomst_invoer.php",
                    api_key = helper_database.get_instelling('API_KEY')
                )
                print(reponse)
                helper_database.insert_doorkomst(
                    id_local = doorkomst["ID_LOCAL"],
                    id_server = reponse["doorkomst"]["DOORKOMST_ID"],
                    datetime = doorkomst["DATETIME"],
                    ploeg = doorkomst["PLOEG"],
                    ETAPPE_VOLGNUMMER = doorkomst["ETAPPE_VOLGNUMMER"],
                    status = "SYNC",
                    evenement_id = doorkomst["EVENEMENT_ID"],
                    local_change = 0
                )
        except:
            print("Error while updating doorkomsten, will try again next time")

def flaskThread(): #function to start local webserver
    webapp.webapp.app.run(host="0.0.0.0", threaded=True, debug = False) #start webserver on all interfaces, with threading enabled and debug mode enabled

# threads ombouwen naar processes, zodat de webserver niet wordt geblokkeerd door de andere taken, en de andere taken niet worden geblokkeerd door de webserver
if __name__ == '__main__':
    config.config_create() #create config file if absent
    on_boot() #action that needs to happen on boot of script
    webapp.webapp.event_trigger = event_trigger #connect the event trigger to the webserver
    threading.Thread(
        target=flaskThread,
        daemon=True).start() #start theard for webserver
    while True:
        event_trigger.wait(timeout=30) #wait for event trigger
        event_trigger.clear() #clear event trigger
        update_live_doorkomsten() #update all doorkomsten which are not yet synced with the server
        update_background() #load all data from the server and insert it in the database
# threading.Thread(target=bufferloop_thread).start() #start thread for background handeling