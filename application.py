from flask import Flask, request
import os
import json
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database


app = Flask(__name__)
file_path = os.path.abspath(os.getcwd())+"\database.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
db = SQLAlchemy(app)

class user(db.Model):
    uid = db.Column(db.Integer,primary_key=True)
    usecret = db.Column(db.String(32), nullable = False) 
    uname = db.Column(db.String(32), nullable = False)
    uemail = db.Column(db.String(80), nullable = False)

    def __repr__(self):
        return f"{self.uid} - {self.usecret} - {self.uname} - {self.uemail}"
class alert(db.Model):
    aid = db.Column(db.Integer,primary_key=True)
    uid = db.Column(db.Integer, nullable = False) 
    atarget = db.Column(db.Integer, nullable = False)
    astatus = db.Column(db.String(80), nullable = False)

    def __repr__(self):
        return f"{self.aid} - {self.uid} - {self.atarget} - {self.astatus}"        

@app.route('/')
def indef():
    response = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false')
    for coins in response.json():
        if(coins["symbol"]=="btc"):
            return str(coins["current_price"])

@app.route('/alerts/create', methods=['POST'])
def add_alert():
    a = alert(uid=request.json["uid"],atarget=request.json["atarget"],astatus="created")
    db.session.add(a)
    db.session.commit()
    return {"a_id":a.aid}

@app.route('/alerts/delete', methods=['PUT'])
def remove_alert():
    r_aid=request.json["aid"]
    row = alert.query.filter_by(aid=r_aid).first()
    row.astatus = "deleted"
    db.session.commit()
    return "Deleted Successfully"

@app.route('/alerts',methods=['GET'])
def view_alerts():
    qf=request.json["queryfilter"]
    if qf=='null':
        alerts = alert.query.filter_by(uid=request.json["uid"]).all()
    else:
        alerts = alert.query.filter_by(uid=request.json["uid"]).filter_by(astatus=qf).all()
    response=[]
    for a in alerts:
        response.append({'aid':a.aid, 'uid':a.uid, 'atarget':a.atarget, 'astatus':a.astatus})
    return {'Alerts':response}
