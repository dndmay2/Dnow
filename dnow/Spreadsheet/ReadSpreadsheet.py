from __future__ import print_function
import httplib2
import os
import sys
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from dateutil.parser import parse
from django.db import DataError
from django.core.exceptions import ObjectDoesNotExist

from dnow.models import *

# https://developers.google.com/sheets/api/quickstart/python

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'
STUDENT_COLUMNS = {}
HOST_COLUMNS = {}
COOK_COLUMNS = {}
LEADER_COLUMNS = {}
DRIVER_COLUMNS = {}
MEAL1 = 'Fri Snacks'
MEAL2 = 'Sat Dinner'


def colToNum(colStr):
    """ Convert base26 column string to number. """
    expn = 0
    col_num = 0
    for char in reversed(colStr):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num - 1


def getCredentials():
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

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        flags = tools.argparser.parse_args(args=[])
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def readCell(row, col):
    # noinspection PyBroadException
    if isinstance(col, str):
        print(col)
    try:
        val = row[col]
    except:
        val = 'NA'
    return val


def getGrade(grade):
    """
    Returns grade without strings in it
    """
    grade = ''.join(c for c in grade if c.isdigit() or c == ',')
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
    elif size in [ '', 'na', '-' ]:
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
    date = parse(val)
    return date


def getMoney(val):
    val = val.replace('$', '')
    if val == '':
        val = 0
    money = float(val)
    return money


class ReadSpreadsheet:
    def __init__(self):
        """Shows basic usage of the Sheets API.

        Creates a Sheets API service object and prints the names and majors of
        students in a sample spreadsheet:
        https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
        """
        self.credentials = getCredentials()
        self.http = self.credentials.authorize(httplib2.Http())
        discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?' 'version=v4'
        self.service = discovery.build('sheets', 'v4', http=self.http, discoveryServiceUrl=discoveryUrl)

        # DNOW: https://docs.google.com/spreadsheets/d/1xb4sfQUGaCT9uDsxhovFl6MCiCR-1AuDPuAj9wJgrcU/edit#gid=0
        # self.spreadsheetId = '1xb4sfQUGaCT9uDsxhovFl6MCiCR-1AuDPuAj9wJgrcU'
        # 2018 DNOW spreadsheet: https://docs.google.com/spreadsheets/d/1pknbr9iBFb-9e-Lt5wiwa74TWl9mJu6d4jVkHtJPV6E/edit#gid=1940584643
        self.spreadsheetId = '1pknbr9iBFb-9e-Lt5wiwa74TWl9mJu6d4jVkHtJPV6E'
        self.hostLastName = self.hostFirstName = self.hostGrade = self.hostGender = self.hostPhone = None
        self.hostEmail = self.hostAddress = self.hostBgCheck = None
        self.cleanup()

    def cleanup(self):
        Meal.objects.all().delete()
        DriveSlot.objects.all().delete()

    def getRangeValues(self, rangeName):
        result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=rangeName).execute()
        values = result.get('values', [])
        return values

    def readStudents(self):
        rangeName = 'Register!A1:AC'
        values = self.getRangeValues(rangeName)

        if not values:
            print('No data found.')
        else:
            Student.objects.all().delete()
            header = values[0]
            data = values[1:]
            self.readColumnHeaders(header, 'students')
            for row in data:
                self.readStudentRow(row)

        for obj in Student.objects.all():
            print('Student', obj)

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

    def readStudentRow(self, row):
        try:
            studentLastName = readCell(row, col=STUDENT_COLUMNS['Student Last Name'])
            studentFirstName = readCell(row, col=STUDENT_COLUMNS['Student First Name'])
            if (studentFirstName and studentFirstName != 'NA') or (studentLastName and studentLastName != 'NA'):
                s = Student(firstName=studentFirstName, lastName=studentLastName)
                s.grade = getGrade(readCell(row, col=STUDENT_COLUMNS['Student Grade']))
                s.gender = getGender(readCell(row, col=STUDENT_COLUMNS['Student Gender']))
                s.phone = readCell(row, col=STUDENT_COLUMNS['Student Cell Number'])
                s.street = readCell(row, col=STUDENT_COLUMNS['Address'])
                s.city = readCell(row, col=STUDENT_COLUMNS['City'])
                s.state = readCell(row, col=STUDENT_COLUMNS['State'])
                s.zip = readCell(row, col=STUDENT_COLUMNS['Zip'])
                # s.medicalForm = getBoolean(readCell(row, col=STUDENT_COLUMNS['']))
                s.dateRegistered = getDate(readCell(row, col=STUDENT_COLUMNS['Date Entered']))
                s.amountPaid = getMoney(readCell(row, col=STUDENT_COLUMNS['Amount']))
                # s.churchMember = getBoolean(readCell(row, col=STUDENT_COLUMNS['']))
                s.tshirtSize = getShirtSize(readCell(row, col=STUDENT_COLUMNS['Student T-shirt Size (adult)']))
                s.friendName = readCell(row, col=STUDENT_COLUMNS['List ONE friend you would like to room with (we will try to accommodate, but we cannot promise to do so)'])
                s.parentPhone = readCell(row, col=STUDENT_COLUMNS['Parent Cell Number'])
                s.parentEmail = readCell(row, col=STUDENT_COLUMNS['Parent Email'])
                hostHome = readCell(row, col=STUDENT_COLUMNS['Host Home'])
                if hostHome:
                    try:
                        hhObj = HostHome.objects.get(lastName=hostHome)
                        s.hostHome = hhObj
                    except:
                        print('No host home for %s %s: .%s.' % (studentFirstName, studentLastName, hostHome))
                s.save()
        except Exception as e:
            print('Error with student row:', row, e)
            print(sys.exc_info())

    def readHosts(self):
        rangeName = 'Host!A2:M'
        values = self.getRangeValues(rangeName)
        if not values:
            print('No data found.')
        else:
            HostHome.objects.all().delete()
            DriveSlot.objects.all().delete()
            header = values[0]
            data = values[1:]
            self.readColumnHeaders(header, 'hosts')
            for row in data:
                self.readHostRow(row)

        for obj in HostHome.objects.all():
            print('Host Home', obj)

    def readHostRow(self, row):
        hh = None
        try:
            hostLastName = readCell(row, col=HOST_COLUMNS['Last Name'])
            hostFirstName = '' # readCell(row, col=HOST_COLUMNS[''])
            if (hostFirstName and hostFirstName != 'NA') or (hostLastName and (hostLastName != 'NA' and hostLastName != '?')):
                hh = HostHome(firstName=hostFirstName, lastName=hostLastName)
                hh.grade = getGrade(readCell(row, col=HOST_COLUMNS['Grades']))
                hh.gender = getGender(readCell(row, col=HOST_COLUMNS['Gender']))
                hh.phone = readCell(row, col=HOST_COLUMNS['Cell'])
                hh.email = readCell(row, col=HOST_COLUMNS['Email'])
                hh.street = readCell(row, col=HOST_COLUMNS['Address'])
                hh.city = readCell(row, col=HOST_COLUMNS['City'])
                hh.state = readCell(row, col=HOST_COLUMNS['State'])
                hh.zip = readCell(row, col=HOST_COLUMNS['Zip'])
                hh.bgCheck = getBoolean(readCell(row, col=HOST_COLUMNS['Background Check?']))
                hh.tshirtSize = getShirtSize(readCell(row, col=HOST_COLUMNS['T-Shirt Size']))
                hh.save()
        except Exception as e:
            print('Error with hosthome row:', row, e)
        if hh:
            for ds in DRIVE_SLOTS:
                driveSlot = DriveSlot(hostHome=hh, time=ds[1])
                driveSlot.save()


    def readCooks(self):
        rangeName = 'Meals!A2:G'
        values = self.getRangeValues(rangeName)

        if not values:
            print('No data found.')
        else:
            Cook.objects.all().delete()
            Meal.objects.all().delete()
            header = values[0]
            data = values[1:]
            self.readColumnHeaders(header, 'cooks')
            for row in data:
                self.readCookRow(row)

        for obj in Cook.objects.all():
            print('Cook', obj)

    def readCookRow(self, row):
        try:
            cookFirstName = readCell(row, col=COOK_COLUMNS['First Name'] )
            cookLastName = readCell(row, col=COOK_COLUMNS['Last Name'] )
            if (cookFirstName and cookFirstName != 'NA') or (cookLastName and cookLastName != 'NA'):
                c = Cook(firstName=cookFirstName, lastName=cookLastName)
                c.phone = readCell(row, col=COOK_COLUMNS['Cell'] )
                c.email = readCell(row, col=COOK_COLUMNS['Email'] )
                meal1 = readCell(row, col=COOK_COLUMNS[MEAL1] )
                hhObj1 = hhObj2 = False
                c.save()
                if meal1 != '' and meal1 != 'NA':
                    try:
                        hhObj1 = HostHome.objects.get(lastName=meal1)
                        m = Meal(cook=c, time=MEAL1, hostHome=hhObj1)
                        m.save()
                        print("Meal = %s" % m)
                    except Exception as e:
                        print('No host home for %s %s meal1: .%s. (%s)' % (cookFirstName, cookLastName, meal1, e))
                meal2 = readCell(row, col=COOK_COLUMNS[MEAL2] )
                if meal2 != '' and meal2 != 'NA':
                    try:
                        hhObj2 = HostHome.objects.get(lastName=meal2)
                        m = Meal(cook=c, time=MEAL2, hostHome=hhObj2)
                        m.save()
                        print("Meal = %s" % m)
                    except Exception as e:
                        print('No host home for %s %s meal2: .%s. (%s)' % (cookFirstName, cookLastName, meal2, e))

        except DataError as e:
            print('Error with cook row:', row, e)


    def readLeaders(self):
        rangeName = 'Leaders!B3:N'
        values = self.getRangeValues(rangeName)

        if not values:
            print('No data found.')
        else:
            Leader.objects.all().delete()
            header = values[0]
            data = values[1:]
            self.readColumnHeaders(header, 'leaders')
            for row in data:
                self.readLeaderRow(row)

        for obj in Leader.objects.all():
            print('Leader', obj)

    def readLeaderRow(self, row):
        try:
            leaderFirstName = readCell(row, col=LEADER_COLUMNS['First Name'] )
            leaderLastName = readCell(row, col=LEADER_COLUMNS['Last Name'] )
            if (leaderFirstName and leaderFirstName != 'NA') or (leaderLastName and leaderLastName != 'NA'):
                ldr = Leader(firstName=leaderFirstName, lastName=leaderLastName)
                ldr.phone = readCell(row, col=LEADER_COLUMNS['Cell'] )
                ldr.email = readCell(row, col=LEADER_COLUMNS['Email'] )
                ldr.tshirtSize = getShirtSize(readCell(row, col=LEADER_COLUMNS['T-Shirt Size']))
                ldr.bgCheck = getBoolean(readCell(row, col=LEADER_COLUMNS['Background Check?']))
                hostHome = readCell(row, col=LEADER_COLUMNS['Host Home'])
                if hostHome:
                    try:
                        hhObj = HostHome.objects.get(lastName=hostHome)
                        ldr.hostHome = hhObj
                    except:
                        print('No host home for %s %s: .%s.' % (leaderFirstName, leaderLastName, hostHome))
                ldr.save()
        except Exception as e:
            print('Error with leader row:', row, e)

    def readDrivers(self):
        rangeName = 'Drivers!A2:M'
        values = self.getRangeValues(rangeName)

        if not values:
            print('No data found.')
        else:
            Driver.objects.all().delete()
            header = values[0]
            data = values[1:]
            self.readColumnHeaders(header, 'drivers')
            for row in data:
                self.readDriverRow(row)

        for obj in Driver.objects.all():
            print('Driver', obj)

    def readDriverRow(self, row):
        try:
            driverFirstName = readCell(row, col=DRIVER_COLUMNS['First Name'] )
            driverLastName = readCell(row, col=DRIVER_COLUMNS['Last Name'] )
            if (driverFirstName and driverFirstName != 'NA') or (driverLastName and driverLastName != 'NA'):
                d = Driver(firstName=driverFirstName, lastName=driverLastName)
                d.phone = readCell(row, col=DRIVER_COLUMNS['Cell'] )
                d.email = readCell(row, col=DRIVER_COLUMNS['Email'] )
                cc = readCell(row, col=DRIVER_COLUMNS['How many can they fit?'])
                if cc == '' or cc == 'NA':
                    print('%s car capacity is unknown! =%s=, defaulting to 3' % (d, cc))
                    d.carCapacity = 3
                else:
                    d.carCapacity = cc
                d.tshirtSize = getShirtSize(readCell(row, col=DRIVER_COLUMNS['T-shirt']))
                d.bgCheck = getBoolean(readCell(row, col=DRIVER_COLUMNS['Background Check?']))
                d.save()
                for ds in DRIVE_SLOTS:
                    time = ds[1]
                    hostHome = readCell(row, col=DRIVER_COLUMNS[time])
                    try:
                        hhObj = HostHome.objects.get(lastName=hostHome)
                        driveSlot = hhObj.driveslot_set.get(time=time)
                        driveSlot.drivers.add(d)
                    except ObjectDoesNotExist:
                        driveSlot = '%s - No hostHome assigned for %s' % (time, d)
                    print(driveSlot)


        except DataError as e:
            print('Error with driver row:', row, e)



if __name__ == '__main__':
    ss = ReadSpreadsheet()
    ss.readStudents()
    ss.readHosts()
