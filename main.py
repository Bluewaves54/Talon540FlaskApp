from flask import Flask, redirect, url_for, request
import pandas
from flask_sqlalchemy import SQLAlchemy
import os

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
    gradyear = db.Column(db.Integer)
    pfp = db.Column(db.String)
    email = db.Column(db.String)


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
            'gradYear': account.gradyear,
            'pfp': account.pfp,
            'email': account.email
        }
    else:
        print('fail')
        return {'output': False}


@app.route('/createNewAccount', methods=['POST'])
def storeInfo():
    try:
        print('before setting variables')
        name = request.args['name']
        deviceID = request.args['deviceID']
        subgroup = request.args['subgroup']
        status = request.args['status']
        gradYear = request.args['gradYear']
        pfp = request.args['pfp']
        email = request.args['email']
        print("after setting variables")
        print(name, deviceID, email, pfp, subgroup, status, gradYear)
        account = User(
            deviceid=deviceID,
            name=name,
            subgroup=subgroup,
            status=status,
            gradyear=gradYear,
            pfp=pfp,
            email=email
        )
        db.session.add(account)
        db.session.commit()
        return {'value': True}
    except:
        return {'value': False}


if __name__ == "__main__":
    app.run()
