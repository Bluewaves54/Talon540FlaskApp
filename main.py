# imports

from flask import Flask, redirect, url_for, request, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from collections import defaultdict
import os
import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd
import datetime
import pytz

# initializing Flask app

app = Flask(__name__)

# configuring database with app

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

# creating database model session

db = SQLAlchemy(app)

NOW = datetime.datetime.now(pytz.timezone('EST'))

# connecting with Google Sheets API

gc = gspread.service_account(filename="talon540sheets-fc00ab1e88d1.json")
sh = gc.open_by_key("12P--EB0GyQdKmmhb0GEiTHZLPaGGP1EfUwHppgkShr0")

# defining User model


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

    @classmethod
    def getByDeviceID(cls, deviceid):
        return cls.query.filter_by(deviceid=deviceid).first()


# defining SignOutTable model


class SignOutTable(db.Model):
    __tablename__ = 'signouttable'

    key = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    room = db.Column(db.String)
    time = db.Column(db.String)

# defining SignInTable model


class SignInTable(db.Model):
    __tablename__ = 'signintable'

    key = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    room = db.Column(db.String)
    time = db.Column(db.String)

# Initializing db session


db.init_app(app)


# function for converting SQLAlchemy query to dictionary for conversion to pandas DataFrame
def query_to_dict(rset):
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)
    return result


@app.route('/')
def homview():
    return "<h1>Welcome to Talon540 App</h1>"


@app.route('/deleteAccount/<string:deviceid>')
def deleteAccount(deviceid):
    account = User.query.filter_by(deviceid=deviceid).first()
    if account is not None:
        db.session.delete(account)
        db.session.commit()
        return {'success': True}
    else:
        return {'success': False}


# @app.route('/checkLogStatus', methods=['POST'])
# def checkLogStatus():
#     data = request.get_json()
#     account = User.query.filter_by(deviceid=data['deviceid']).first()
#     print(account)
#     currentSOTable = SignOutTable.query.all()
#     print(currentSOTable)
#     occurencesOfSO = 0
#     for i in currentSOTable:
#         if i.name == account.name:
#             occurencesOfSO += 1
#
#     print(occurencesOfSO)
#
#     currentSITable = SignInTable.query.all()
#     print(currentSITable)
#     occurencesOfSI = 0
#     for i in currentSITable:
#         if i.name == account.name:
#             occurencesOfSI += 1
#
#     print(occurencesOfSI)
#
#     if occurencesOfSI > occurencesOfSO:
#         return {'output': 'signout'}
#     elif occurencesOfSO == occurencesOfSI:
#         return {'output': 'signin'}


@app.route('/writeToSheets/signOutTable', methods=['POST'])
def writeToSheetsSignOutTable():
    global NOW, gc, sh

    data = request.get_json()

    account = User.query.filter_by(deviceid=data['deviceid']).first()

    if datetime.datetime.now(pytz.timezone('EST')).day != NOW.day:
        db.session.query(SignInTable).delete()
        db.session.query(SignOutTable).delete()
        db.session.commit()

        NOW = datetime.datetime.now(pytz.timezone('EST'))

    entry = SignOutTable(
        name=account.name,
        room=data['room'],
        time=datetime.datetime.now(pytz.timezone('EST')).time()
    )

    db.session.add(entry)
    db.session.commit()

    SOdf = pd.DataFrame(query_to_dict(SignOutTable.query.all()))

    try:
        worksheet = sh.worksheet(f'Day {NOW.day}')
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=f'Day {NOW.day}', rows=500, cols=10)
        worksheet.update('A1', 'Sign In')
        worksheet.update('F1', 'Sign Out')
        worksheet.format('A1:F1', {'textFormat': {'bold': True}})
    set_with_dataframe(worksheet, SOdf, row=2, col=6)

    print(worksheet.id)

    return {
        'spreadsheet_key': '12P--EB0GyQdKmmhb0GEiTHZLPaGGP1EfUwHppgkShr0',
        'worksheet_key': worksheet.id
    }


@app.route('/writeToSheets/signInTable', methods=['POST'])
def writeToSheetsSignInTable():
    global NOW, gc, sh

    data = request.get_json()

    account = User.query.filter_by(deviceid=data['deviceid']).first()

    if datetime.datetime.now(pytz.timezone('EST')).day != NOW.day:
        db.session.query(SignInTable).delete()
        db.session.query(SignOutTable).delete()
        db.session.commit()

        NOW = datetime.datetime.now(pytz.timezone('EST'))

    entry = SignInTable(
        name=account.name,
        room=data['room'],
        time=datetime.datetime.now(pytz.timezone('EST')).time()
    )

    db.session.add(entry)
    db.session.commit()

    SIdf = pd.DataFrame(query_to_dict(SignInTable.query.all()))

    try:
        worksheet = sh.worksheet(f'Day {NOW.day}')
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=f'Day {NOW.date()}', rows=500, cols=10)
        worksheet.update('A1', 'Sign In')
        worksheet.update('F1', 'Sign Out')
        worksheet.format('A1:F1', {'textFormat': {'bold': True}})
    set_with_dataframe(worksheet, SIdf, row=2)

    print(worksheet.id)

    return {
        'spreadsheet_key': '12P--EB0GyQdKmmhb0GEiTHZLPaGGP1EfUwHppgkShr0',
        'worksheet_key': worksheet.id
    }


@app.route('/fetchInformation/', methods=['POST'])
def fetchInformation():
    data = request.get_json()
    account = User.query.filter_by(deviceid=data['deviceid']).first()
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


@app.route('/updateInfo', methods=['POST'])
def updateInfo():
    data = request.get_json()
    account = User.query.filter_by(deviceid=data['deviceid']).first()
    account.notifmethod = data['notifmethod']
    account.subgroup = data['subgroup']
    account.status = data['status']
    db.session.add(account)
    db.session.commit()
    return {'output': True}


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
            'notifmethod': account.notifmethod,
            'email': account.email
        }
        print(user)
        return_data[account.name] = user

    return return_data


if __name__ == "__main__":
    app.run()
