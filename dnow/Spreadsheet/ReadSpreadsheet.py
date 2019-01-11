from __future__ import print_function
# import httplib2
import os
import sys
from apiclient import discovery
# import json
import simplejson
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from dateutil.parser import parse
from django.db import DataError
from django.core.exceptions import ObjectDoesNotExist
# from django.conf import settings
from google.oauth2 import service_account

from dnow.models import *
import dnow.config
from decouple import config

# https://developers.google.com/sheets/api/quickstart/python

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
# Using a service account:
# https://medium.com/@denisluiz/python-with-google-sheets-service-account-step-by-step-8f74c26ed28e
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')
CLIENT_SECRET = config('CLIENT_SECRET')
APPLICATION_NAME = 'Google Sheets API Python Quickstart'
STUDENT_COLUMNS = {}
HOST_COLUMNS = {}
COOK_COLUMNS = {}
LEADER_COLUMNS = {}
DRIVER_COLUMNS = {}
MEAL1 = 'Fri Snacks - 9:30PM'
MEAL2 = 'Sat Dinner - 5:00PM'


def printLog(s):
    print(s)
    dnow.config.SPREADSHEET_LOG += s + '\n'


def colToNum(colStr):
    """ Convert base26 column string to number. """
    expn = 0
    col_num = 0
    for char in reversed(colStr):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num - 1


def getCredentials(user):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')
    os.remove(credential_path)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES, login_hint=user.profile.googleDriveEmail)
        flow.user_agent = APPLICATION_NAME
        flags = tools.argparser.parse_args(args=[])
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        printLog('Storing credentials to ' + credential_path)
    return credentials


def readCell(row, col):
    # noinspection PyBroadException
    if isinstance(col, str):
        printLog(col)
    try:
        val = row[col].strip()
    except:
        val = 'NA'
    return val


def getGrade(grade):
    """
    Returns grade without strings in it
    """
    grade = ''.join(c for c in grade if c.isdigit() or c == ',' or c == '-')
    if grade == '':
        grade = '?'
    return grade


def getGender(gender):
    gender = gender.lower()
    if gender in ['f', 'female', 'girl', 'girls', 'femail', 'g', 'lady', 'woman', 'women']:
        return 'F'
    else:
        return 'M'


def getShirtSize(size):
    size = size.lower()
    size = size.replace('adult ', '')
    if size in ['m', 'med', 'medium']:
        return 'M'
    elif size in ['l', 'large', 'lrg', 'lrge']:
        return 'L'
    elif size in ['s', 'sm', 'small']:
        return 'S'
    elif size in ['xl', 'extra large', 'xtra large', 'x-large', 'xtra-large', 'xlarge', 'x large']:
        return 'XL'
    elif size in ['xxl', '2xl', 'double xl', 'xx-large']:
        return 'XXL'
    elif size in ['xxxl', '3xl', 'triple xl', 'xxx-large']:
        return 'XXXL'
    elif size in ['', 'na', '-']:
        return '-'
    elif ',' in size:
        sizes = size.split(',')
        newSizes = []
        for s in sizes:
            newSizes.append(getShirtSize(s.strip()))
        return ', '.join(newSizes)
    else:
        return size + '?'


def getBoolean(val):
    val = val.lower()
    if val in ['y', 'yes', 'true', 'ok', 'x']:
        return True
    else:
        return False


def getDate(val):
    try:
        date = parse(val)
    except ValueError:
        date = '1999-01-01'
    return date


def getMoney(val):
    val = val.replace('$', '')
    if val == '':
        val = 0
    money = float(val)
    return money


def getAllergy(val):
    val = val.lower()
    if val == 'none' or val == 'na':
        val = ''
    val = val.replace('/', ',')
    return val


def checkFriendAgainstSet(friends, students):
    yes = []
    no = []
    for friend in friends.split(','):
        friend = friend.strip()
        if ' ' in friend:
            try:
                firstName, lastName = friend.split()
            except ValueError:
                print('ERROR: Separate friend names with commas: %s' % friend)
                firstName = lastName = ''
            f1 = students.filter(firstName=firstName, lastName=lastName).first()
            if f1:
                yes.append(f1.lastName)
            else:
                # print('f1.%s.' % friend)
                no.append(friend)
        else:
            f2 = students.filter(lastName=friend).first()
            if f2:
                yes.append(f2.lastName)
            else:
                f3 = students.filter(firstName=friend).first()
                if f3:
                    yes.append(f3.lastName)
                else:
                    # print('f3.%s.' % friend)
                    no.append(friend)
    return yes, no


def checkStudentFriendMatchups(user):
    hostHomesList = HostHome.objects.exclude(grade__contains='?').filter(user=user).order_by('lastName')
    allStudents = Student.objects.filter(user=user).all()
    friendDict = {}
    for hh in hostHomesList:
        # for hh in [hostHomesList.first()]:
        print('------------------------------------------------------------------------------')
        print('HOST HOME: %s Grade: %s Gender: %s' % (hh.lastName, hh.grade, hh.gender))
        hhStudents = hh.student_set.all().order_by('lastName')
        for student in hhStudents:
            friends = student.friendName.strip()
            if friends:
                yes, no = checkFriendAgainstSet(friends, hhStudents)
            else:
                yes = []
                no = []
            other = ''
            flag = ''
            if no and not yes:
                yes2, no2 = checkFriendAgainstSet(friends, allStudents)
                if yes2:
                    other = '%s found elsewhere' % '.'.join(yes2)
                else:
                    other = '%s not registered' % ('.'.join(no2))
                if yes2:
                    flag = '**'
            print('%2s %-10s %-12s : YES: %-20s\t NO: %-20s OTHER: %s' %
                  (flag, student.firstName, student.lastName, ','.join(yes), ','.join(no), other))
            friendDict[student] = [','.join(yes), ','.join(no), other]
    return friendDict


class ReadSpreadsheet:
    def __init__(self, user):
        """Shows basic usage of the Sheets API.

        Creates a Sheets API service object and prints the names and majors of
        students in a sample spreadsheet:
        https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
        """
        dnow.config.SPREADSHEET_LOG = ''
        self.user = user
        self.spreadsheetId = None
        self.parseSpreadSheetUrl()

        # OLD
        # self.credentials = getCredentials(user)
        # self.http = self.credentials.authorize(httplib2.Http())
        # discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?' 'version=v4'
        # self.service = discovery.build('sheets', 'v4', http=self.http, discoveryServiceUrl=discoveryUrl)

        # NEW
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file",
                  "https://www.googleapis.com/auth/spreadsheets"]
        # secret_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')
        print(CLIENT_SECRET[:50], CLIENT_SECRET[-50:], len(CLIENT_SECRET))
        secret_file = simplejson.loads(CLIENT_SECRET)

        # credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        credentials = service_account.Credentials.from_service_account_info(secret_file)
        self.service = discovery.build('sheets', 'v4', credentials=credentials.with_scopes(scopes))

        # DNOW: https://docs.google.com/spreadsheets/d/1xb4sfQUGaCT9uDsxhovFl6MCiCR-1AuDPuAj9wJgrcU/edit#gid=0
        # self.spreadsheetId = '1xb4sfQUGaCT9uDsxhovFl6MCiCR-1AuDPuAj9wJgrcU'
        # 2018 DNOW spreadsheet: https://docs.google.com/spreadsheets/d/1pknbr9iBFb-9e-Lt5wiwa74TWl9mJu6d4jVkHtJPV6E/edit#gid=1940584643
        # self.spreadsheetId = '1pknbr9iBFb-9e-Lt5wiwa74TWl9mJu6d4jVkHtJPV6E'
        self.hostLastName = self.hostFirstName = self.hostGrade = self.hostGender = self.hostPhone = None
        self.hostEmail = self.hostAddress = self.hostBgCheck = None
        self.currentColumn = self.currentTable = None
        self.cleanup()

    def cleanup(self):
        Meal.objects.filter(user=self.user).all().delete()
        DriveSlot.objects.filter(user=self.user).all().delete()

    def parseSpreadSheetUrl(self):
        """
        https://docs.google.com/spreadsheets/d/1pknbr9iBFb-9e-Lt5wiwa74TWl9mJu6d4jVkHtJPV6E/edit#gid=1940584643
        :return: 1pknbr9iBFb-9e-Lt5wiwa74TWl9mJu6d4jVkHtJPV6E
        """
        urlPath = self.user.profile.googleSpreadSheet
        parts = urlPath.split('/')
        if len(parts) >= 6 and (parts[0] == 'https:' or parts[0] == 'http:'):
            self.spreadsheetId = parts[5]
        elif len(parts) >= 4 and parts[0] == 'docs.google.com':
            self.spreadsheetId = parts[3]
        else:
            self.spreadsheetId = None
            printLog('**ERROR: Not a valid Google Spreadsheet path: %s' % urlPath)
        printLog('spreadSheetId = %s' % self.spreadsheetId)

    def getRangeValues(self, rangeName):
        result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=rangeName).execute()
        values = result.get('values', [])
        return values

    def readStudents(self):
        rangeName = 'Register!A1:AF'
        printLog('\nReading students from %s' % rangeName)
        values = self.getRangeValues(rangeName)

        if not values:
            printLog('No data found.')
        else:
            Student.objects.filter(user=self.user).all().delete()
            header = values[0]
            data = values[1:]
            self.readColumnHeaders(header, 'students')
            for row in data:
                self.readStudentRow(row)

        for obj in Student.objects.filter(user=self.user).all():
            printLog('Student: %s' % obj)

    def readColumnHeaders(self, header, table):
        colNum = 0
        for c in header:
            if table == 'students':
                STUDENT_COLUMNS[c] = colNum
            elif table == 'hosts':
                HOST_COLUMNS[c] = colNum
            elif table == 'cooks':
                COOK_COLUMNS[c] = colNum
            elif table == 'leaders':
                LEADER_COLUMNS[c] = colNum
            elif table == 'drivers':
                DRIVER_COLUMNS[c] = colNum
            colNum += 1

    def getColNum(self, table, col):
        if table == 'students':
            colNum = STUDENT_COLUMNS[col]
        elif table == 'hosts':
            colNum = HOST_COLUMNS[col]
        elif table == 'cooks':
            colNum = COOK_COLUMNS[col]
        elif table == 'leaders':
            colNum = LEADER_COLUMNS[col]
        elif table == 'drivers':
            colNum = DRIVER_COLUMNS[col]
        self.currentColumn = col
        self.currentTable = table
        return colNum

    def isValidName(self, name):
        name = name.lower()
        if name == 'na':
            return False
        elif name == '':
            return False
        elif name == '-':
            return False
        elif name == '?':
            return False
        elif name == "leaders who are driving":
            return False
        else:
            return True

    def readStudentRow(self, row):
        try:
            studentLastName = readCell(row, col=self.getColNum('students', 'Student Last Name'))
            if studentLastName == 'Byland':
                pass
            studentFirstName = readCell(row, col=self.getColNum('students', 'Student First Name'))
            if self.isValidName(studentFirstName)  or self.isValidName(studentLastName):
                s = Student(firstName=studentFirstName, lastName=studentLastName)
                s.grade = getGrade(readCell(row, col=self.getColNum('students', 'Student Grade')))
                s.gender = getGender(readCell(row, col=self.getColNum('students', 'Student Gender')))
                s.phone = readCell(row, col=self.getColNum('students', 'Student Cell #'))
                s.street = readCell(row, col=self.getColNum('students', 'Address'))
                s.city = readCell(row, col=self.getColNum('students', 'City'))
                s.state = readCell(row, col=self.getColNum('students', 'State'))
                s.zip = readCell(row, col=self.getColNum('students', 'Zip'))
                s.medicalForm = getBoolean(readCell(row, col=self.getColNum('students', 'Waiver')))
                s.dateRegistered = getDate(readCell(row, col=self.getColNum('students', 'Date Entered')))
                s.amountPaid = getMoney(readCell(row, col=self.getColNum('students', 'Amount')))
                s.tshirtSize = getShirtSize(readCell(row, col=self.getColNum('students', 'Student T-Shirt Size')))
                s.friendName = readCell(row, col=self.getColNum('students', 'Friend'))
                s.parentPhone = readCell(row, col=self.getColNum('students', 'Parent Cell #'))[:20]
                s.parentEmail = readCell(row, col=self.getColNum('students', 'Parent Email'))
                s.allergy = getAllergy(readCell(row, col=self.getColNum('students', 'Allergy')))
                s.user = self.user
                hostHome = readCell(row, col=self.getColNum('students', 'Host Home'))
                if hostHome:
                    try:
                        hhObj = HostHome.objects.filter(user=self.user).get(lastName=hostHome)
                        s.hostHome = hhObj
                    except:
                        printLog('No host home for %s %s: .%s.' % (studentFirstName, studentLastName, hostHome))
                s.save()
        except Exception as e:
            printLog('Error with student row: %s\n    %s = %s' % (row, self.currentColumn, e))
            print(sys.exc_info())

    def readHosts(self):
        rangeName = 'Host!A2:M'
        printLog('\nReading hosts from %s' % rangeName)
        values = self.getRangeValues(rangeName)
        if not values:
            printLog('No data found.')
        else:
            HostHome.objects.filter(user=self.user).all().delete()
            DriveSlot.objects.filter(user=self.user).all().delete()
            header = values[0]
            data = values[1:]
            self.readColumnHeaders(header, 'hosts')
            for row in data:
                self.readHostRow(row)

        for obj in HostHome.objects.filter(user=self.user).all():
            printLog('Host Home: %s' % obj)

    def readHostRow(self, row):
        hh = None
        try:
            hostLastName = readCell(row, col=HOST_COLUMNS['Last Name'])
            hostFirstName = '' # readCell(row, col=HOST_COLUMNS[''])
            if self.isValidName(hostFirstName) or self.isValidName(hostLastName):
                hh = HostHome(firstName=hostFirstName, lastName=hostLastName)
                hh.grade = getGrade(readCell(row, col=HOST_COLUMNS['Grades']))
                hh.gender = getGender(readCell(row, col=HOST_COLUMNS['Gender']))
                hh.phone = readCell(row, col=HOST_COLUMNS['Cell'])
                hh.email = readCell(row, col=HOST_COLUMNS['Email'])
                hh.street = readCell(row, col=HOST_COLUMNS['Address'])
                hh.city = readCell(row, col=HOST_COLUMNS['City'])
                hh.state = readCell(row, col=HOST_COLUMNS['State'])
                hh.zipCode = readCell(row, col=HOST_COLUMNS['Zip'])
                hh.bgCheck = getBoolean(readCell(row, col=HOST_COLUMNS['Background Check?']))
                hh.tshirtSize = getShirtSize(readCell(row, col=HOST_COLUMNS['T-Shirt Size']))
                hh.allergy = getAllergy(readCell(row, col=HOST_COLUMNS['Allergy']))
                hh.color = readCell(row, col=HOST_COLUMNS['Color'])
                hh.user = self.user
                hh.save()
        except Exception as e:
            printLog('Error with hosthome row: %s %s' % (row, e))
        if hh:
            for ds in DRIVE_SLOTS:
                driveSlot = DriveSlot(hostHome=hh, time=ds[1])
                driveSlot.user = self.user
                driveSlot.save()


    def readCooks(self):
        rangeName = 'Meals!A2:G'
        printLog('\nReading cooks from %s' % rangeName)
        values = self.getRangeValues(rangeName)

        if not values:
            printLog('No data found.')
        else:
            Cook.objects.filter(user=self.user).all().delete()
            Meal.objects.filter(user=self.user).all().delete()
            header = values[0]
            data = values[1:]
            self.readColumnHeaders(header, 'cooks')
            for row in data:
                self.readCookRow(row)

        for obj in Cook.objects.filter(user=self.user).all():
            printLog('Cook: %s' % obj)

    def readCookRow(self, row):
        try:
            cookFirstName = readCell(row, col=COOK_COLUMNS['First Name'] )
            cookLastName = readCell(row, col=COOK_COLUMNS['Last Name'] )
            if self.isValidName(cookFirstName) or self.isValidName(cookLastName):
                c = Cook(firstName=cookFirstName, lastName=cookLastName)
                c.phone = readCell(row, col=COOK_COLUMNS['Cell'] )
                c.email = readCell(row, col=COOK_COLUMNS['Email'] )
                meal1 = readCell(row, col=COOK_COLUMNS[MEAL1] )
                hhObj1 = hhObj2 = False
                c.user = self.user
                c.save()
                if meal1 != '' and meal1 != 'NA':
                    try:
                        hhObj1 = HostHome.objects.filter(user=self.user).get(lastName=meal1)
                        m = Meal(cook=c, time=MEAL1, hostHome=hhObj1)
                        m.user = self.user
                        m.save()
                        printLog("Meal = %s" % m)
                    except Exception as e:
                        printLog('No host home for %s %s meal1: .%s. (%s)' % (cookFirstName, cookLastName, meal1, e))
                meal2 = readCell(row, col=COOK_COLUMNS[MEAL2] )
                if meal2 != '' and meal2 != 'NA':
                    try:
                        hhObj2 = HostHome.objects.filter(user=self.user).get(lastName=meal2)
                        m = Meal(cook=c, time=MEAL2, hostHome=hhObj2)
                        m.user = self.user
                        m.save()
                        printLog("Meal = %s" % m)
                    except Exception as e:
                        printLog('No host home for %s %s meal2: .%s. (%s)' % (cookFirstName, cookLastName, meal2, e))

        except DataError as e:
            printLog('Error with cook row: %s %s' % (row, e))


    def readLeaders(self):
        rangeName = 'Leaders!B3:N'
        printLog('\nReading leaders from %s' % rangeName)
        values = self.getRangeValues(rangeName)

        if not values:
            printLog('No data found.')
        else:
            Leader.objects.filter(user=self.user).all().delete()
            header = values[0]
            data = values[1:]
            self.readColumnHeaders(header, 'leaders')
            for row in data:
                self.readLeaderRow(row)

        for obj in Leader.objects.filter(user=self.user).all():
            printLog('Leader: %s' % obj)

    def readLeaderRow(self, row):
        try:
            leaderFirstName = readCell(row, col=LEADER_COLUMNS['First Name'] )
            leaderLastName = readCell(row, col=LEADER_COLUMNS['Last Name'] )
            if self.isValidName(leaderFirstName) or self.isValidName(leaderLastName):
                ldr = Leader(firstName=leaderFirstName, lastName=leaderLastName)
                ldr.phone = readCell(row, col=LEADER_COLUMNS['Cell'] )
                ldr.email = readCell(row, col=LEADER_COLUMNS['Email'] )
                ldr.tshirtSize = getShirtSize(readCell(row, col=LEADER_COLUMNS['T-Shirt Size']))
                ldr.bgCheck = getBoolean(readCell(row, col=LEADER_COLUMNS['Background Check?']))
                ldr.isDriving = getBoolean(readCell(row, col=LEADER_COLUMNS['Driving?']))
                ldr.allergy = getAllergy(readCell(row, col=LEADER_COLUMNS['Allergy']))
                hostHome = readCell(row, col=LEADER_COLUMNS['Host Home'])
                if hostHome:
                    if hostHome == 'Church Staff':
                        ldr.churchStaff = True
                    else:
                        try:
                            hhObj = HostHome.objects.filter(user=self.user).get(lastName=hostHome)
                            ldr.hostHome = hhObj
                        except:
                            printLog('No host home for %s %s: .%s.' % (leaderFirstName, leaderLastName, hostHome))
                ldr.user = self.user
                ldr.save()
        except Exception as e:
            printLog('Error with leader row: %s %s' % (row, e))

    def readDrivers(self):
        rangeName = 'Drivers!A2:O'
        printLog('\nReading drivers from %s' % rangeName)
        values = self.getRangeValues(rangeName)

        if not values:
            printLog('No data found.')
        else:
            Driver.objects.filter(user=self.user).all().delete()
            header = values[0]
            data = values[1:]
            self.readColumnHeaders(header, 'drivers')
            for row in data:
                self.readDriverRow(row)

        for obj in Driver.objects.filter(user=self.user).all():
            printLog('Driver: %s' % obj)

    def readDriverRow(self, row):
        try:
            driverFirstName = readCell(row, col=DRIVER_COLUMNS['First Name'] )
            driverLastName = readCell(row, col=DRIVER_COLUMNS['Last Name'] )
            if self.isValidName(driverFirstName) or self.isValidName(driverLastName):
                d = Driver(firstName=driverFirstName, lastName=driverLastName)
                d.phone = readCell(row, col=DRIVER_COLUMNS['Cell'] )
                d.email = readCell(row, col=DRIVER_COLUMNS['Email'] )
                cc = readCell(row, col=DRIVER_COLUMNS['How many can they fit?'])
                if cc == '' or cc == 'NA':
                    printLog('%s car capacity is unknown! =%s=, defaulting to 3' % (d, cc))
                    d.carCapacity = 4
                else:
                    d.carCapacity = cc
                d.tshirtSize = getShirtSize(readCell(row, col=DRIVER_COLUMNS['T-shirt']))
                d.bgCheck = getBoolean(readCell(row, col=DRIVER_COLUMNS['Background Check?']))
                d.user = self.user
                d.save()
                for ds in DRIVE_SLOTS:
                    time = ds[1]
                    hostHome = readCell(row, col=DRIVER_COLUMNS[time])
                    try:
                        hhObj = HostHome.objects.filter(user=self.user).get(lastName=hostHome)
                        driveSlot = hhObj.driveslot_set.get(time=time)
                        driveSlot.drivers.add(d)
                    except ObjectDoesNotExist:
                        driveSlot = '%s - No hostHome assigned for %s' % (time, d)
                    printLog('%s' % driveSlot)


        except DataError as e:
            printLog('Error with driver row: %s %s' % (row, e))



if __name__ == '__main__':
    ss = ReadSpreadsheet()
    ss.readStudents()
    ss.readHosts()
