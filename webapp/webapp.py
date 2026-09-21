from flask import Flask, render_template, request, redirect, url_for
from flask.config import Config 
import datetime
import time
import ast
import csv

import helper_database #import the database_init of the app

app = Flask(__name__)

event_trigger = None #event trigger for background tasks, will be set in main.py

@app.context_processor
def inject_status():
    return {
        "event_status": "Open",
        "checkpoint_status": "Open"
    }

@app.route('/')
def home():
    title = "Systeem"

    evenement_id = helper_database.get_instelling('EVENEMENT_ID')
    etappe_volgnummer = helper_database.get_instelling('ETAPPE_VOLGNUMMER')

    config_load =  {
            "API_key": helper_database.get_instelling('API_KEY'),
            "API_competitioninfo": helper_database.get_instelling('API_competitioninfo'),
            "API_events": helper_database.get_instelling('API_events'),
            "EVENEMENT_ID": evenement_id,
            "ETAPPE_VOLGNUMMER": helper_database.get_instelling('ETAPPE_VOLGNUMMER'),
            "ETAPPE_NAAM": helper_database.get_instelling('WISSELPUNT_NAAM'),
            "checkpointteam": helper_database.get_instelling('checkpointteam'),
            "checkpointteam_list": ["wppA", "wppB", "wppC", "wppD"],
            "ETAPPE_LIST": helper_database.get_wisselpunten(evenement_id),
            "local_ip": helper_database.get_instelling('local_ip'),
            "hostname": helper_database.get_instelling('hostname')
        }
    
    # build doorkomsten
    doorkomsten = helper_database.get_doorkomsten(evenement_id, etappe_volgnummer)
        
    # build missende ploegen
    missende_ploeg = helper_database.get_missende_ploegen(evenement_id, etappe_volgnummer)
    ploegen = helper_database.get_ploeglijst(evenement_id)
    return render_template("systeem_status.html", title = title, config_load = config_load, doorkomsten = doorkomsten, missende_ploegen = missende_ploeg, ploegen = ploegen)

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

        if event_trigger is not None:
            event_trigger.set() #trigger the background tasks to upload the new doorkomst
            print("Event trigger set, background tasks will be executed")
        else:
            print(">>> ERROR: event_trigger is not connected!")

    return render_template("invoeren_doorkomst.html", title= title)

@app.route("/doorkomsten_fragment")
def doorkomsten_fragment():

    evenement_id = helper_database.get_instelling('EVENEMENT_ID')
    etappe_volgnummer = helper_database.get_instelling('ETAPPE_VOLGNUMMER')

    doorkomsten = helper_database.get_doorkomsten(evenement_id, etappe_volgnummer)

    missende_ploeg = helper_database.get_missende_ploegen(evenement_id, etappe_volgnummer)
    missende_ploeg_len = len(missende_ploeg)
    ploegen_len = len(helper_database.get_ploeglijst(evenement_id))
    
    return render_template("table_doorkomst.html", doorkomsten=doorkomsten[:5], missende_ploeg=missende_ploeg, missende_ploeg_len=missende_ploeg_len, ploegen_len=ploegen_len)

@app.route("/invoerenwijziging", methods = ['POST', 'GET'])
def invoerenwijzging():
    title = "Invoeren Wijzigingen"

    if request.method == 'POST':
        if request.form['action'] == "doorkomst":
            ploegNummer = request.form['team_insert']
            evenement_id = helper_database.get_instelling('EVENEMENT_ID')
            etappeVolgnummer = helper_database.get_instelling('ETAPPE_VOLGNUMMER')
            datetime_current = (request.form['time_insert'] + request.form['timezone'])
            datetime_current = datetime.datetime.fromisoformat(datetime_current).isoformat()

            # insert doorkomt in database
            helper_database.insert_doorkomst(
                datetime = datetime_current, 
                ploeg = ploegNummer, 
                ETAPPE_VOLGNUMMER = etappeVolgnummer, 
                status = "NOSYNC", 
                evenement_id = evenement_id,   
            )

            if event_trigger is not None:
                event_trigger.set() #trigger the background tasks to upload the new doorkomst
                print("Event trigger set, background tasks will be executed")
            else:
                print(">>> ERROR: event_trigger is not connected!")

        if request.form['action'] == "mv":
            ploegNummer = request.form['team_insert_mv']
            evenement_id = helper_database.get_instelling('EVENEMENT_ID')
            etappeVolgnummer = helper_database.get_instelling('ETAPPE_VOLGNUMMER')
            datetime_current = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat() #current system datetime

            # insert doorkomt in database
            helper_database.insert_consequentie(
                datetime = datetime_current, 
                ploeg = ploegNummer, 
                ETAPPE_VOLGNUMMER = etappeVolgnummer, 
                status = "NOSYNC", 
                evenement_id = evenement_id,   
            )
            
            if event_trigger is not None:
                event_trigger.set() #trigger the background tasks to upload the new doorkomst
                print("Event trigger set, background tasks will be executed")
            else:
                print(">>> ERROR: event_trigger is not connected!")

        else:
            print("else") 

    return render_template("invoeren_handmatig.html", title= title)

# grote update nodig
@app.route("/wijzigingen")
def wijzigingen():
    title = "Wijzigingen"
    return render_template("wijzigingen.html", title= title)

@app.route("/instellingen", methods=['GET', 'POST'])
def instellingen():
    title = "Instellingen"

    if request.method == 'POST':

        action = request.form.get("action")

        # ==========================================
        # FORM 1: Event/API instellingen
        # ==========================================
        if action == "event":
            evenement_id = int(request.form['EVENEMENT_ID'])
            helper_database.insert_instelling('API_KEY', request.form['API_key'])
            helper_database.insert_instelling('API_competitioninfo', request.form['API_competitioninfo'])
            helper_database.insert_instelling('API_events', request.form['API_events'])
            helper_database.insert_instelling('EVENEMENT_ID', evenement_id)

            if event_trigger is not None:
                event_trigger.set() #trigger the background tasks to upload the new doorkomst
                print("Event trigger set, background tasks will be executed")
            else:
                print(">>> ERROR: event_trigger is not connected!")

            return redirect(url_for("instellingen"))

        # ==========================================
        # FORM 2: Etappe instellingen
        # ==========================================
        elif action == "etappe":

            etappe_volgnummer = int(request.form['etappe_volgnummer'])
            evenement_id = helper_database.get_instelling('EVENEMENT_ID')
            wisselpunt_naam = helper_database.get_wisselpunt_by_etappe(evenement_id, etappe_volgnummer)
            helper_database.insert_instelling('ETAPPE_VOLGNUMMER', etappe_volgnummer)
            helper_database.insert_instelling('WISSELPUNT_NAAM', wisselpunt_naam)
            helper_database.insert_instelling('checkpointteam', request.form['checkpointteam'])

            if event_trigger is not None:
                event_trigger.set() #trigger the background tasks to upload the new doorkomst
                print("Event trigger set, background tasks will be executed")
            else:
                print(">>> ERROR: event_trigger is not connected!")

            return redirect(url_for("instellingen"))

    # ==========================================
    # GET: load current settings
    # ==========================================

    evenement_id = helper_database.get_instelling('EVENEMENT_ID')
    instelling_huidig = {
        "API_key": helper_database.get_instelling('API_KEY'),
        "API_competitioninfo": helper_database.get_instelling('API_competitioninfo'),
        "API_events": helper_database.get_instelling('API_events'),
        "EVENEMENT_ID": evenement_id,
        "ETAPPE_VOLGNUMMER": helper_database.get_instelling('ETAPPE_VOLGNUMMER'),
        "ETAPPE_NAAM": helper_database.get_instelling('WISSELPUNT_NAAM'),
        "checkpointteam": helper_database.get_instelling('checkpointteam'),
        "checkpointteam_list": ["wppA", "wppB", "wppC", "wppD"],
        "ETAPPE_LIST": helper_database.get_wisselpunten(evenement_id)
    }

    return render_template("instellingen.html", title=title, config_load=instelling_huidig)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True)