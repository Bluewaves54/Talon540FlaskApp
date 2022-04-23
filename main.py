# imports
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from collections import defaultdict
import os
import datetime
import pytz
import users
import attendance as att
import inventory as inv
# initializing Flask app
app = Flask(__name__)
# configuring database with app
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
# creating database model session
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

# defining Inventory Items model

# class Item(db.Model):
#     __tablename__ = 'inventory'
#
#     key = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     company = db.Column(db.Integer)
#     cost = db.Column(db.Float)
#     location = db.Column(db.Integer)
#     type = db.Column(db.Integer)
#     count = db.Column(db.Integer)

# defining Manufacturing Company model

class ManuComp(db.Model):
    __tablename__ = 'manufacturingcompanies'

    key = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.Integer)
    address = db.Column(db.String)
    website = db.Column(db.String)

NOW = datetime.datetime.now(pytz.timezone('EST'))
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
def homeview():
    return "<h1>Welcome to Talon540 App</h1>"


@app.route('/users', methods=['GET', 'POST'])
def allUserEndpoints():
    data = request.get_json()
    try:
        if data['function'] == 'deleteAccount':
            return users.deleteAccount(data)
        elif data['function'] == 'viewAccounts':
            return users.viewAccounts(data)
        elif data['function'] == 'storeInfo':
            return users.storeInfo(data)
        elif data['function'] == 'updateInfo':
            return users.updateInfo(data)
        elif data['function'] == 'fetchInformation':
            return users.fetchInformation(data)
        else:
            return {'value': 'function not found'}
    except Exception as e:
        return {'error': str(e)}


@app.route('/attendance', methods=['GET', 'POST'])
def allAttendanceEndpoints():
    data = request.get_json()
    try:
        if data['function'] == 'returnSpreadsheetKey':
            return att.returnSpreadsheetKey(data)
        elif data['function'] == 'writeToSheets':
            return att.writeToSheets(data)
        else:
            return {'value': 'function not found'}
    except Exception as e:
        return {'value': 'no function specified'}

@app.route('/inventory', methods=['GET', 'POST'])
def allInventoryEndpoints():
    data = request.get_json()
    return inv.returnTable()

if __name__ == "__main__":
    app.run()
