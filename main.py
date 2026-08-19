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

def on_boot():
#    print('boot')
    helper_database.create_tables() # build database if it doesnt exist yet
    update_background() #load all data from the server and insert it in the database

    # choose how to select the primiary event
    # read all data from the server and insert it in the database
    
    #below here is old
    config_all = config.config_read()
    config.config_write(config_all)

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


def flaskThread(): #function to start local webserver
    webapp.webapp.app.run(host="0.0.0.0", threaded=True, debug = False) #start webserver on all interfaces, with threading enabled and debug mode enabled


# heeft nog een grote update nodig, wordt de functie waarin alle achtergrond taken worden uitgevoerd, zoals het uploaden van data die niet gelukt is bij de eerste poging, en het downloaden van nieuwe data van de cloud
def bufferloop_thread():  
    while True: #start endless loop

        # interval for all background actions, like uploading data which failed on the original attempt, and downloading new data from the cloud
        update_interval = config.config_read()["system"]["update_interval"] #get current update interval

        # get lost off all failed uploads
        try:
            doorkomsten_list = []
            for doorkomst in doorkomsten_list:
                # insert_doorkomst(EVENEMENT_ID, etappeVolgnummer, ploegNummer, doorkomstTijd, api, api_key)
                pass
        except:
            print("Failed to upload doorkomsten")

        #functie voor het opvragen van alle doorkomsten van de cloud
        try:
            helper_api.load_doorkomsten()
        except:
            print("Failed to load doorkomsten")

        try:
            helper_api.load_competitioninfo()
        except:
            print("Failed to load competition info")

        time.sleep(update_interval) #wait update interval
        

# threads ombouwen naar processes, zodat de webserver niet wordt geblokkeerd door de andere taken, en de andere taken niet worden geblokkeerd door de webserver
if __name__ == '__main__':
    config.config_create() #create config file if absent
    on_boot() #action that needs to happen on boot of script
    threading.Thread(target=flaskThread).start() #start theard for webserver
    while True:
        update_background()
        time.sleep(1)

# threading.Thread(target=bufferloop_thread).start() #start thread for background handeling