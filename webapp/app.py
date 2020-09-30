from flask import Flask
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
import requests

import threading

import datetime
import time #for sleeping

# start/stop
import RPi.GPIO as GPIO
import subprocess

# for RFID reader
import usb.core
import usb.util
import sys

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/pi/veluweloop_db_0_1.db"
db = SQLAlchemy(app)

db.Model.metadata.reflect(db.engine)

class Checkpoint(db.Model):
    __tablename__ = "checkpoint"
    __table_args__ = { "extend_existing": True }
    id = db.Column(db.Text, primary_key=True)
    
class Doorkomst(db.Model):
    __tablename__ = "doorkomst"
    __table_args__ = { "extend_existing": True }
    id = db.Column(db.Integer, primary_key=True)
    ploeg = db.Column(db.Text)
    tijd = db.Column(db.Text)
    type = db.Column(db.Text)
    wisselpunt = db.Column(db.Text)
    wisselpuntploeg = db.Column(db.Text)
    serialid = db.Column(db.Text)


class Transponder(db.Model):
    __tablename__ = "transponder"
    __table_args__ = { "extend_existing": True }
    id = db.Column(db.Integer, primary_key=True)
    tagid = db.Column(db.Text)
    ploeg = db.Column(db.Text)
    
class Instellingen(db.Model):
    __tablename__ = "instellingen"
    __table_args__ = { "extend_existing": True }
    id = db.Column(db.Integer, primary_key=True)
    serialid = db.Column(db.Text)
    wisselpuntploeg = db.Column(db.Text)
    wisselpunt = db.Column(db.Text)

def getserial():
    cpuserial = 'ERROR000000000'
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = 'ERROR000000000'
    return cpuserial

serialid = getserial()

def JSON_POST(ploeg, tijd, bron, locatie):

    API_ENDPOINT = "https://httpbin.org/post"
                
    data_json = {
        'ploeg':ploeg,
        'tijd':tijd,
        'type':bron,
        'locatie':locatie                    
        }
                
    r = requests.post(url = API_ENDPOINT, data = data_json)
                
    pastebin_url = r.text
    print("The pastebin URL is:%s"%pastebin_url)


@app.route("/")
def index():
    instellingen_db = Instellingen.query.filter_by(serialid = serialid).order_by(Instellingen.id.desc()).first()
    
    checkpointteam_name = instellingen_db.wisselpuntploeg
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M:%S")
    
    templateData = {
        "title" : "Veluweloop",
        "time" : timeString,
        "serialid" : serialid,
        "checkpointteam_name" : checkpointteam_name,
        "current_checkpoint" : instellingen_db.wisselpunt,
        "count" : Checkpoint.query.count(),
        "WP" : Checkpoint.query.all(),
        #"Doorkomst_top10" : Doorkomst.query.order_by(Doorkomst.tijd.desc()).limit(10).all()
        }
    
    return render_template("index.html", **templateData)

@app.route("/InvoerenDoorkomst/", methods=["GET", "POST"])
def invoeren_doorkomst():
    instellingen_db = Instellingen.query.filter_by(serialid = serialid).order_by(Instellingen.id.desc()).first()
    now = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    timeString = now.strftime("%Y-%m-%d %H:%M:%S")
    templateData = {
        "title" : "Invoeren Doorkomst",
        #"Doorkomst_top10" : Doorkomst.query.order_by(Doorkomst.tijd.desc()).limit(10).all()
        }
    
    if request.form.get("team_insert") != None:
        ploeg = "???"
        if request.form.get("team_insert") != "":
            ploeg = request.form.get("team_insert")
        
        #send data to webserver
        JSON_POST(ploeg, now, "MANUAL", instellingen_db.wisselpunt)
        
        #save data locally 
        new_record = Doorkomst(tijd = now, ploeg = ploeg, type = 'MANUAL', wisselpunt = instellingen_db.wisselpunt, wisselpuntploeg = instellingen_db.wisselpuntploeg, serialid = instellingen_db.serialid)
            
        db.session.add(new_record)
        db.session.commit()
    
    return render_template("InvoerenDoorkomst.html", **templateData)

@app.route("/Instellingen/", methods=["GET", "POST"])
def instellingen():
    instellingen_db = Instellingen.query.filter_by(serialid = serialid).order_by(Instellingen.id.desc()).first()
        
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M:%S")
    checkpointteam_name = instellingen_db.wisselpuntploeg
    templateData = {
        "title" : "Instellingen",
        "serialid" : serialid,
        "checkpointteam_name" : checkpointteam_name,
        "current_checkpoint" : instellingen_db.wisselpunt,  
        "checkpoints" : Checkpoint.query.all()
        }
    if request.form.get("WPP_naam") != None:
        new_record = Instellingen(serialid = serialid, wisselpuntploeg = request.form.get("WPP_naam"), wisselpunt = request.form.get("checkpoint_select"))
            
        db.session.add(new_record)
        db.session.commit()
        
        print(request.form.get("checkpoint_select"))
        print(request.form.get("WPP_naam"))
    
    
    return render_template("Instellingen.html", **templateData)

def flaskThread():
    app.run(host="0.0.0.0", threaded=True)
    
    
# Thread for rebooting system from switch
def Thread2():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.wait_for_edge(3, GPIO.FALLING)
    
    subprocess.call(['shutdown', '-h', 'now'], shell=False) 
    
# Extra Thread for read rfid
def Thread3():
    test = usb.core.find(idVendor = 6790, idProduct=57360)

    interface = 0
    endpoint = test[0][(0,0)][0]

    if test.is_kernel_driver_active(interface) is True:
        test.detach_kernel_driver(interface)
        usb.util.claim_interface(test, interface)

    while True:
        try:
            data = test.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
            
            if " ".join(map(str, data[0:2])) == "31 67":
            
                result = " ".join(map(str, data[18:30]))
            
                now = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    
                # print(now, " ", result)
                # print(data)
            
                ploeg_input = "???"
                tagTOploeg = Transponder.query.filter_by(tagid = result).first()
                instellingen_db = Instellingen.query.filter_by(serialid = serialid).order_by(Instellingen.id.desc()).first()
            
                if tagTOploeg is None:
                    ploeg = "???"
                else:
                    ploeg_input = tagTOploeg.ploeg
            
                
                #send data tro database
                JSON_POST(ploeg_input, now, "AUTO", instellingen_db.wisselpunt)
                
                
                #save data locally
                new_record = Doorkomst(tijd = now, ploeg = ploeg_input, type = 'AUTO', wisselpunt = instellingen_db.wisselpunt, wisselpuntploeg = instellingen_db.wisselpuntploeg, serialid = instellingen_db.serialid)
                        
                db.session.add(new_record)
                db.session.commit()
            
                print(now, " ", ploeg_input, " ", 'gelukt')
                        
            
        except usb.core.USBError as e:
            data = None
            if e.args == ('Operation timed out', ):
            
                Continue



if __name__ == "__main__":
    threading.Thread(target=flaskThread, args=()).start() #start the flask server
#     Thread2() #start the second Thread
    Thread3() #start the third Thread
    


