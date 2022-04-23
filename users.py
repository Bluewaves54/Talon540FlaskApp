import main

def deleteAccount(data):
    account = main.User.query.filter_by(deviceid=data['deviceid']).first()
    if account is not None:
        main.db.session.delete(account)
        main.db.session.commit()
        return {'success': True}
    else:
        return {'success': False}

def fetchInformation(data):
    deviceid = data['deviceID']
    account = main.User.query.filter_by(deviceid=deviceid).first()
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

def updateInfo(data):
    account = main.User.query.filter_by(deviceid=data['deviceid']).first()
    account.notifmethod = (data['notifmethod'] if data['notifmethod'] is not None else account.notifmethod)
    account.subgroup = (data['subgroup'] if data['subgroup'] is not None else account.subgroup)
    account.status = (data['status'] if data['status'] is not None else account.status)
    main.db.session.add(account)
    main.db.session.commit()
    return {'output': True}

def storeInfo(data):
    try:
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
        account = main.User(
            deviceid=deviceID,
            name=name,
            subgroup=subgroup,
            status=status,
            pfp=pfp,
            email=email,
            notifmethod=notifmethod
        )
        main.db.session.add(account)
        main.db.session.commit()
        return {'value': True}

    except:
        return {'value': False}

def viewAccounts(data):
    accounts = main.User.query.all()
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
