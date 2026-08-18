from flask import Flask, render_template, request
from flask.config import Config 
import datetime
import time
import ast
import csv

import helper_database #import the database_init of the app
import config #import the config of the app
import main #import the main.py file

app = Flask(__name__)

class webserver:
    buffer = []
    def __init___(self):
        pass            

@app.route('/')
def home():
    title = "Systeem"
    config_load = config.config_read()

    # doorkomsten
    filename = config_load["system"]["filename_registration"] #get file_name from config
    with open(filename,'r') as f: 
        csv_reader = csv.reader(f, delimiter=',')
        doorkomsten = list(csv_reader)
        doorkomsten.sort(reverse=True)
        doorkomsten = filter(lambda c: c[4] == str(config_load["competition"]["checkpoint"]["ETAPPE_VOLGNUMMER"]) and c[5] == str(config_load["competition"]["EVENEMENT_ID"]), doorkomsten)
        

    # missende ploegen
    filename = config_load["system"]["filename_registration"] #get file_name from config
    with open(filename,'r') as f: 
        csv_reader = csv.reader(f, delimiter=',')
        doorkomsten_2 = list(csv_reader)
        doorkomsten_2 = filter(lambda c: c[4] == str(config_load["competition"]["checkpoint"]["ETAPPE_VOLGNUMMER"]) and c[5] == str(config_load["competition"]["EVENEMENT_ID"]), doorkomsten_2)
        ploeglijst = config_load["competition"]["team_list"]
        doorkomst_list = []
        missende_ploeg = []
        
        # build doorkomsten
        for record in doorkomsten_2:
            doorkomst_list.append(record[2])	

        # build doorkomsten_online list
        doorkomsten_online = config_load["competition"]["doorkomsten"]
        for doorkomst in doorkomsten_online:
            if str(doorkomst["ETAPPE_VOLGNUMMER"]) == str(config_load["competition"]["checkpoint"]["ETAPPE_VOLGNUMMER"]):
                doorkomst_list.append(str(doorkomst["STARTNUMMER"])[:3]) 

        # build missende ploegen
        for ploeg in ploeglijst:
            if str(ploeg["PLOEGNUMMER"]) not in doorkomst_list:
                missende_ploeg.append(ploeg)
        
    return render_template("systeem_status.html", title = title, config_load = config_load, doorkomsten = doorkomsten, missende_ploeg = missende_ploeg)

@app.route("/invoerendoorkomst", methods = ['POST', 'GET'])
def invoerendoorkomst():
    title = "Doorkomst"

    if request.method == 'POST':
        ploegNummer = request.form['team_insert']
        datetime_current = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat() #current system datetime
        evenement_id = helper_database.get_instelling('EVENEMENT_ID')
        etappeVolgnummer = helper_database.get_instelling('ETAPPE_VOLGNUMMER')
        
        # insert doorkomt in database
        helper_database.insert_doorkomst(
            datetime = datetime_current, 
            ploeg = ploegNummer, 
            ETAPPE_VOLGNUMMER = etappeVolgnummer, 
            status = "NOSYNC", 
            evenement_id = evenement_id,   
        )

    config_load = config.config_read()

    return render_template("invoeren_doorkomst.html", title= title)

@app.route("/doorkomsten_fragment")
def doorkomsten_fragment():
    config_load = config.config_read()

    # doorkomsten
    filename = config_load["system"]["filename_registration"] #get file_name from config
    with open(filename,'r') as f: 
        csv_reader = csv.reader(f, delimiter=',')
        doorkomsten = list(csv_reader)
        doorkomsten.sort(reverse=True)
        doorkomsten = filter(lambda c: c[4] == str(config_load["competition"]["checkpoint"]["ETAPPE_VOLGNUMMER"]) and c[5] == str(config_load["competition"]["EVENEMENT_ID"]), doorkomsten)

    return render_template("table_doorkomst.html", doorkomsten=doorkomsten)

@app.route("/invoerenwijziging", methods = ['POST', 'GET'])
def invoerenwijzging():
    title = "Invoeren Wijzigingen"

    if request.method == 'POST':
        if request.form['action'] == "doorkomst":
            team = request.form['team_insert']
            datetime_current = (request.form['time_insert'] + request.form['timezone'])
            datetime_current = datetime.datetime.strptime(datetime_current, '%Y-%m-%dT%H:%M:%S%z').isoformat()

            buffer_temp = (datetime_current, team, "NA") #combine al data into a single variable

            webserver().buffer.append(buffer_temp) 

        if request.form['action'] == "mv":
            team = request.form['team_insert_mv']
            datetime_current = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat() #current system datetime

            buffer_temp = (datetime_current, team, "MV")
        
            webserver().buffer.append(buffer_temp)

        else:
            print("else")

#           print(datetime_current, " ", team)
#           print(webserver().buffer)
        

    return render_template("invoeren_handmatig.html", title= title)

@app.route("/wijzigingen")
def wijzigingen():
    title = "Wijzigingen"
    return render_template("wijzigingen.html", title= title)

@app.route("/instellingen", methods = ['POST', 'GET'])
# alle instellingen staan komen nu in de database. Dit betreffen minimaal de volgende instellingen: API-Key, EVENEMENT_ID, LOCATIE_ID, WISSELPUNTPLOEG
#onderstaanden functie en bijbehorend html bestand moeten nog aangepast worden zodat de instellingen in de database worden gezet en niet meer in de config.json file. De config.json file wordt alleen nog gebruikt voor systeem instellingen, zoals update interval, battery status, internet status etc.
def instellingen():
    title = "Instellingen"
    config_load = config.config_read()

    if request.method == 'POST':
        
        config_load["competition"]["checkpointteam"] = request.form['checkpointteam']
        config_load["competition"]["checkpoint"] = ast.literal_eval(request.form['checkpoint'])
        config_load["competition"]["ETAPPE_VOLGNUMMER"] = config_load["competition"]["checkpoint"]["ETAPPE_VOLGNUMMER"]

        config.config_write(config_load)

        
    return render_template("instellingen.html", title= title, config_load = config_load)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True)