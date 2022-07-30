from flask import Flask, request, jsonify, make_response
import os
import json
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import getpass
import requests
import jwt
import datetime
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database


app = Flask(__name__)
file_path = os.path.abspath(os.getcwd())+"\database.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
app.config['SECRET_KEY']='ToTheMoooonnnnn'
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

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'access_token' in request.headers:
            token = request.headers['access_token']
        if not token:
            return jsonify({'Response':'Token is missing'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = user.query.filter_by(uid=data['uid']).first()
        except:
            return jsonify({'Response':'Invalid Token'})
        
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def indef():
    response = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false')
    for coins in response.json():
        if(coins["symbol"]=="btc"):
            return str(coins["current_price"])

@app.route('/user',methods=['POST'])
def create_user():
    hashed_usecret = generate_password_hash(request.json["password"], method='sha256')
    db.session.add(user(usecret=hashed_usecret, uname=request.json["username"], uemail=request.json["email"]))
    db.session.commit()
    return {"Response":"New user created"}

@app.route('/login')
def user_login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response("Please enter username and password", 401, {"WWW-Authenticate":"Basic Realm='Login Failed'"})
    user_row = user.query.filter_by(uname=auth.username).first()
    if not user_row:
        return make_response("Wrong username or password", 401, {"WWW-Authenticate":"Basic Realm='Login Failed'"})
    if check_password_hash(user_row.usecret, auth.password):
        token = jwt.encode({'uid':user.uid, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
        return jsonify({'token':token.decode(  'UTF-8')})

    return make_response("Wrong username or password", 401, {"WWW-Authenticate":"Basic Realm='Login Failed'"})

@app.route('/alerts/create', methods=['POST'])
@token_required
def add_alert(current_user):
    a = alert(uid=request.json["uid"],atarget=request.json["atarget"],astatus="created")
    db.session.add(a)
    db.session.commit()
    return {"a_id":a.aid}

@app.route('/alerts/delete', methods=['PUT'])
@token_required
def remove_alert(current_user):
    r_aid=request.json["aid"]
    row = alert.query.filter_by(aid=r_aid).first()
    row.astatus = "deleted"
    db.session.commit()
    return "Deleted Successfully"

@app.route('/alerts',methods=['GET'])
@token_required
def view_alerts(current_user):
    qf=request.json["queryfilter"]
    if qf=='null':
        alerts = alert.query.filter_by(uid=request.json["uid"]).all()
    else:
        alerts = alert.query.filter_by(uid=request.json["uid"]).filter_by(astatus=qf).all()
    response=[]
    for a in alerts:
        response.append({'aid':a.aid, 'uid':a.uid, 'atarget':a.atarget, 'astatus':a.astatus})
    return {'Alerts':response}

def send_email():
    msg = MIMEMultipart()
    password = your_password
    msg['From'] = your_email
    msg['To']=send_email_to
    msg['Subject'] = "BTC Price has reached target. ACT Accordingly."

    message = "Dear client" + your_name + "\nBitcoin price has now crossed the target of: " + str(bitcoin_rate) + ". Time to Sell? \nRegards\nYour friendly neighborhoodly crypto alert API"
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'],msg['To'], message)
    server.quit()

    print("Alert has successfully been triggered, changing status now.")

your_name=""
your_email="enter email"
your_password="enter password"
#can use getpass for security i guess, hardcoding here for now
send_email_to=""
alert_amount=""
bitcoin_rate=25000

@app.route('/sendEmails')
def theInfiniteLoop():
    while True:
        url= "https://api.coindesk.com/v1/bpi/currentprice.json"
        response1 = requests.get(
            url,headers={"Accept":"application/json"},)
        data = response1.json()    
        bpi=data['bpi']
        USD=bpi['USD']
        bitcoin_rate=int(USD['rate_float'])
        targetList = alert.query.filter(alert.atarget <= bitcoin_rate).filter(alert.astatus == 'created').all()
        for targetRow in targetList:
            userRow = user.query.filter_by(uid=targetRow.uid).first()
            send_email_to=userRow.uemail
            your_name=userRow.uname
            send_email()
            targetRow.astatus = 'triggered'
            db.session.commit()
            print("Ctrl + C to quit, will check again in 5 minutes.")        
        
        print('Price is ' + str(bitcoin_rate) + '. Will check again in 5 minutes. Ctrl + C to exit.')
        time.sleep(300)
