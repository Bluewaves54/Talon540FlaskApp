from flask import Flask, redirect, url_for, request, g, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    deviceid = db.Column(db.String)
    name = db.Column(db.String)
    subgroup = db.Column(db.String)
    status = db.Column(db.String)
    pfp = db.Column(db.String)
    email = db.Column(db.String)
    notifmethod = db.Column(db.String)

db.init_app(app)


@app.route('/')
def homview():
    return "<h1>Welcome to Talon540 App</h1>"


@app.route('/addName/<string:name>')
def addName(name):
    global current_name
    current_name = name
    print(current_name)
    if name == '':
        return {'output': False}
    else:
        return {'output': True}


@app.route('/deleteAccount/<string:deviceID>')
def deleteAccount(deviceID):
    account = User.query.filter_by(deviceid=deviceID).first()
    if account is not None:
        db.session.delete(account)
        db.session.commit()
        return {'success': True}
    else:
        return {'success': False}


@app.route('/fetchInformation/<string:deviceID>')
def fetchInformation(deviceID):
    account = User.query.filter_by(deviceid=deviceID).first()
    print(account)
    if account is not None:
        print('success')
        print()
        return {
            'deviceID': account.deviceid,
            'name': account.name,
            'subgroup': account.subgroup,
            'status': account.status,
            'pfp': account.pfp,
            'email': account.email,
            'notifmethod': account.notifmethod
        }
    else:
        print('fail')
        return {'output': False}


@app.route('/createNewAccount', methods=['POST'])
def storeInfo():
    try:
        data = request.get_json()
        print('before setting variables')
        name = data['name']
        deviceID = data['deviceID']
        subgroup = data['subgroup']
        status = data['status']
        pfp = data['pfp']
        email = data['email']
        notifmethod = data['notifmethod']
        # if name or deviceID or subgroup or
        print("after setting variables")
        print(name, deviceID, email, pfp, subgroup, status)
        account = User(
            deviceid=deviceID,
            name=name,
            subgroup=subgroup,
            status=status,
            pfp=pfp,
            email=email,
            notifmethod=notifmethod
        )
        db.session.add(account)
        db.session.commit()
        return {'value': True}

    except:
        return {'value': False}


@app.route('/viewAccounts')
def viewAccounts():
    accounts = User.query.all()
    return_data = {}
    for account in accounts:
        user = {
            'name': account.name,
            'subgroup': account.subgroup,
            'status': account.status,
            'gradYear': account.gradyear,
            'email': account.email
        }
        print(user)
        return_data[account.name] = user

    return return_data


@app.route('/changeNotifMethod', methods=['POST'])
def changeNotifMethod():
    data = request.get_json()
    account = User.query.filter_by(deviceid=data['deviceid']).first()
    account.notifmethod = data['notifMethod']
    db.session.add(account)
    db.session.commit()
    return {'output': True}




if __name__ == "__main__":
    app.run()
