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

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

db = SQLAlchemy(app)

NOW = datetime.datetime.now(pytz.timezone('EST'))

gc = gspread.service_account(filename="talon540sheets-fc00ab1e88d1.json")
sh = gc.open_by_key("12P--EB0GyQdKmmhb0GEiTHZLPaGGP1EfUwHppgkShr0")


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


class SignOutTable(db.Model):
    __tablename__ = 'signouttable'

    name = db.Column(db.String, primary_key=True)
    room = db.Column(db.String)
    time = db.Column(db.String)


class SignInTable(db.Model):
    __tablename__ = 'signintable'

    name = db.Column(db.String, primary_key=True)
    room = db.Column(db.String)
    time = db.Column(db.String)


db.init_app(app)


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
        time=NOW.time()
    )

    db.session.add(entry)
    db.session.commit()

    currentSOTable = db.session.query(SignOutTable).all()

    print(currentSOTable)

    currentSOdict = query_to_dict(currentSOTable)

    SOdf = pd.DataFrame(currentSOdict)

    print(SOdf)

    try:
        worksheet = sh.worksheet(f'Day {NOW.day}')
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=f'Day {NOW.day}', rows=500, cols=10)
        worksheet.update('B1', 'Sign In')
        worksheet.update('F1', 'Sign Out')
        worksheet.format('A1:F1', {'textFormat': {'bold': True}})
    set_with_dataframe(worksheet, SOdf, row=2, col=5)

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
        time=NOW.time()
    )

    db.session.add(entry)
    db.session.commit()

    currentSITable = db.session.query(SignInTable).all()

    currentSIdict = query_to_dict(currentSITable)

    SIdf = pd.DataFrame(currentSIdict)

    try:
        worksheet = sh.worksheet(f'Day {NOW.day}')
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=f'Day {NOW.day}', rows=500, cols=10)
        worksheet.update('B1', 'Sign In')
        worksheet.update('F1', 'Sign Out')
        worksheet.format('A1:F1', {'textFormat': {'bold': True}})
    set_with_dataframe(worksheet, SIdf, row=2)

    return {
        'spreadsheet_key': '12P--EB0GyQdKmmhb0GEiTHZLPaGGP1EfUwHppgkShr0',
        'worksheet_key': worksheet.id
    }


@app.route('/fetchInformation/<string:deviceid>')
def fetchInformation(deviceid):
    account = User.query.filter_by(deviceid=deviceid).first()
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
