import json
import os
import datetime
import csv

# if no json settings file is found use empty dict
# create function for this
def config_create():
    if os.path.exists("config.json") == False:
        settings = dict({
            "competition" : dict({
                "EVENEMENT_ID": "Na",
                "ETAPPE_VOLGNUMMER": "Na",
                "LOCATIE_ID": "Na",
                "checkpointteam" : "Na",
                "checkpointteam_list" : "Na",
                "checkpoint" : "Na",
                "checkpoint_list" : "Na"
            }),
            "system" : dict({
                "id" : "Na",
                "battery" : "Na",
                "internet": "Na",
                "update_interval" : 1,
                "RFID_reader": "Na",
                "filename_registration" : "Na",
                "filename_RFIDtagToTeam": "Na"
            }),
            "database" : dict({
                "host":  "Na",
                "user": "Na",
                "password": "Na",
                "database": "Na",
                "charset": "Na"
            }),    
            "log" : dict({
                "update_last" : "Na",
                "record_last" : "Na",
            })
        })

        with open('config.json', 'w') as outfile:
            json.dump(settings, outfile, indent = 4)


# read json file for all settings
def config_read():
    with open('config.json') as json_file:
        config = json.load(json_file)
    return(config)

# write json file for all settings
def config_write(config):
    log(config)

    with open('config.json', 'w') as outfile:
        json.dump(config, outfile, indent = 4)

# logging of config
def log(config_new):
    config_old = config_read()

    datetime_current = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat() #current system datetime

    for key_1 in config_old.keys():
        for key_2 in config_old[key_1].keys():
            if config_old[key_1].get(key_2) != config_new[key_1].get(key_2):
                log_record = [datetime_current, key_1, key_2, config_old[key_1].get(key_2), config_new[key_1].get(key_2)]
                with open('log.csv','a') as f:
                    writer = csv.writer(f)
                    writer.writerow(log_record)