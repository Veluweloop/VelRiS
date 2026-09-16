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

# hier staan de externe tools welke worden geimporteerd. Helper scripts zijn ondersteunend en de webbapp is the flask server
import webapp.webapp #local webserver for entering manual data
import helper_database #import the database_init of the app
import helper_api #import helpder function for api interaction with external servers

event_trigger = threading.Event() #create event trigger for background tasks

def on_boot():
#    print('boot')
    helper_database.create_tables() # build database if it doesnt exist yet
    update_background() #load all data from the server and insert it in the database

# functie voor het synchroniseren van de algemene informatie van een evenement, zoals de etappes en de ploegen
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

    # ping to webserver
    helper_api.ping_webserver(
        WPP_name = helper_database.get_instelling('checkpointteam'),
        event_id = helper_database.get_instelling('EVENEMENT_ID'),
        checkpoint_id = helper_database.get_instelling('ETAPPE_VOLGNUMMER'),
        ping_interval = 30,
        api = "https://veluweloop.nl/api/ping.php",
        api_key = helper_database.get_instelling('API_KEY')
    )

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
        time.sleep(0.5)

def update_consequenties():
    consequenties_local = helper_database.get_consequenties()
    for consequentie in consequenties_local:
        try:
            if consequentie["STATUS"] == "NOSYNC":
                print(consequentie)
                reponse = helper_api.insert_consequentie_mv(
                    EVENEMENT_ID = consequentie["EVENEMENT_ID"],
                    etappeVolgnummer = consequentie["ETAPPE_VOLGNUMMER"],
                    ploegNummer = consequentie["PLOEG"],
                    api = "https://veluweloop.nl/api/invoer_consequentie.php",
                    api_key = helper_database.get_instelling('API_KEY')
                )
                print(reponse)
                helper_database.insert_consequentie(
                    id_local = consequentie["ID_LOCAL"],
                    ploeg = consequentie["PLOEG"],
                    ETAPPE_VOLGNUMMER = consequentie["ETAPPE_VOLGNUMMER"],
                    status = "SYNC",
                    evenement_id = consequentie["EVENEMENT_ID"]
                )
        except:
            print("Error while updating consequenties, will try again next time")

        time.sleep(0.5)


def flaskThread(): #function to start local webserver
    webapp.webapp.app.run(host="0.0.0.0", threaded=True, debug = False) #start webserver on all interfaces, with threading enabled and debug mode enabled

# threads ombouwen naar processes, zodat de webserver niet wordt geblokkeerd door de andere taken, en de andere taken niet worden geblokkeerd door de webserver
if __name__ == '__main__':
    on_boot() #action that needs to happen on boot of script
    webapp.webapp.event_trigger = event_trigger #connect the event trigger to the webserver
    threading.Thread(
        target=flaskThread,
        daemon=True).start() #start theard for webserver
    while True:
        event_trigger.wait(timeout=30) #wait for event trigger
        event_trigger.clear() #clear event trigger
        update_live_doorkomsten() #update all doorkomsten which are not yet synced with the server
        update_consequenties()
        update_background() #load all data from the server and insert it in the database
# threading.Thread(target=bufferloop_thread).start() #start thread for background handeling