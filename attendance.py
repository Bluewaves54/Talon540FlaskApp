from flask import request
import pytz
import datetime
import main
import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd

SPREADSHEET_CREDENTIALS = "talon540sheets-fc00ab1e88d1.json"
SPREADSHEET_KEY = "12P--EB0GyQdKmmhb0GEiTHZLPaGGP1EfUwHppgkShr0"
gc = gspread.service_account(filename=SPREADSHEET_CREDENTIALS)
sh = gc.open_by_key(SPREADSHEET_KEY)

def returnSpreadsheetKey(data):
    global NOW, gc, sh
    if datetime.datetime.now(pytz.timezone('EST')).day != NOW.day:
        main.db.session.query(main.SignInTable).delete()
        main.db.session.query(main.SignOutTable).delete()
        main.db.session.commit()

        NOW = datetime.datetime.now(pytz.timezone('EST'))
    try:
        worksheet = sh.worksheet(f'Day {data["date"]}')
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=[]|f"Day {data['date']}", rows=500, cols=10)
        worksheet.update('A1', 'Sign In')
        worksheet.update('F1', 'Sign Out')
        worksheet.format('A1:F1', {'textFormat': {'bold': True}})

    return {
        'spreadsheet_key': '12P--EB0GyQdKmmhb0GEiTHZLPaGGP1EfUwHppgkShr0',
        'worksheet_key': worksheet.id
    }

def writeToSheets(data):
    global NOW, gc, sh
    print(NOW, sh, gc)

    account = main.User.query.filter_by(deviceid=data['deviceid']).first()
    print(account)

    if datetime.datetime.now(pytz.timezone('EST')).day != NOW.day:
        main.db.session.query(main.SignInTable).delete()
        main.db.session.query(main.SignOutTable).delete()
        main.db.session.commit()

        NOW = datetime.datetime.now(pytz.timezone('EST'))
        print(NOW)

    if data['table'] == 'signOut':
        entry = main.SignInTable(
            name=account.name,
            room=data['room'],
            time=datetime.datetime.now(pytz.timezone('EST')).time()
        )
        print(entry)
    else:
        entry = main.SignInTable(
            name=account.name,
            room=data['room'],
            time=datetime.datetime.now(pytz.timezone('EST')).time()
        )
        print(entry)

    main.db.session.add(entry)
    main.db.session.commit()

    if data['table'] == 'signOut':
        df = pd.DataFrame(main.query_to_dict(main.SignInTable.query.all()))
        print(df)
    else:
        df = pd.DataFrame(main.query_to_dict(main.SignInTable.query.all()))
        print(df)

    try:
        worksheet = sh.worksheet(f'Day {NOW.date()}')
        print(worksheet)
    except gspread.exceptions.WorksheetNotFound:
        main.SignInTable.query.delete()
        main.db.session.commit()
        main.SignOutTable.query.delete()
        main.db.session.commit()
        worksheet = sh.add_worksheet(title=f'Day {NOW.date()}', rows=500, cols=10)
        worksheet.update('A1', 'Sign In')
        worksheet.update('F1', 'Sign Out')
        worksheet.format('A1:F1', {'textFormat': {'bold': True}})
        print(worksheet)
    set_with_dataframe(worksheet, df, row=2)

    print(worksheet.id)

    return {
        'spreadsheet_key': '12P--EB0GyQdKmmhb0GEiTHZLPaGGP1EfUwHppgkShr0',
        'worksheet_key': worksheet.id
    }
