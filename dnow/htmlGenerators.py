from django.db.models import Sum
from django.urls import reverse
from django.template.loader import render_to_string
from django.template.loader import get_template

from tabulate import tabulate

from dnow.models import *
from collections import defaultdict
from dnow.Spreadsheet.ReadSpreadsheet import checkStudentFriendMatchups

import re


def stripHtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


class Tshirts():
    def __init__(self, hostHome):
        self.tshirtCounts = defaultdict(lambda: 0)
        self.hostHome = hostHome

    def countShirts(self):
        self.getHostHomeShirts()
        self.getLeaderShirts()
        self.getStudentShirts()
        # print(self.hostHome, self.tshirtCounts)

    def getHostHomeShirts(self):
        sizeString = self.hostHome.tshirtSize.replace(' ', '')
        sizes = sizeString.split(',')
        for size in sizes:
            self.tshirtCounts[size] += 1

    def getLeaderShirts(self):
        for leader in self.hostHome.leader_set.all():
            self.tshirtCounts[leader.tshirtSize] += 1

    def getStudentShirts(self):
        for student in self.hostHome.student_set.all():
            self.tshirtCounts[student.tshirtSize] += 1

    def createTshirtTable(self):
        headers = [ x[1] for x in SHIRT_SIZES ]
        headers.append('Total')
        tshirtTable = [headers]
        count = 0
        row = []
        for size in SHIRT_SIZES:
            num = self.tshirtCounts[size[1]]
            count += num
            row.append(num)
        row.append(count)
        tshirtTable.append(row)
        return tshirtTable


def generateShirtSizesHtml(hostHome):
    ts = Tshirts(hostHome)
    ts.countShirts()
    data = ts.createTshirtTable()
    html = tabulate(data[1:], headers=data[0], tablefmt='html')
    text = tabulate(data[1:], headers=data[0], tablefmt='grid')
    return html, text


def generateShirtSizesSummaryHtml(tshirtCounts):
    ts = Tshirts(None)
    ts.tshirtCounts = tshirtCounts
    data = ts.createTshirtTable()
    html = tabulate(data[1:], headers=data[0], tablefmt='html')
    return html


def generateLeadersTable(hostHome):
    leaders = hostHome.leader_set.all()
    table = [['Name', 'Phone', 'T Shirt Size', 'Allergies']]
    for leader in leaders:
        row = []
        row.append('%s %s' % (leader.firstName, leader.lastName))
        row.append(leader.phone)
        row.append(leader.tshirtSize)
        row.append(leader.allergy)
        table.append(row)
    return table


def generateLeadersHtml(hostHome):
    data = generateLeadersTable(hostHome)
    html = tabulate(data[1:], headers=data[0], tablefmt='html')
    text = tabulate(data[1:], headers=data[0], tablefmt='grid')
    return html, text


def generateAllStudentHtmlTable():
    studentList = Student.objects.order_by('hostHome__lastName', 'grade', 'lastName')
    table = [['Name', 'Gender', 'Grade', 'Host Home', 'Matched Friends', 'Unmatched Friends', 'Why' ]]
    friendDict = checkStudentFriendMatchups()
    for student in studentList:
        row = ['%s %s' % (student.firstName, student.lastName)]
        row.append(student.gender)
        row.append(student.grade)
        try:
            row.append(student.hostHome.lastName)
        except:
            row.append('none')
        try:
            row.append(friendDict[student][0])
        except:
            row.append('none')
        try:
            row.append(friendDict[student][1])
        except:
            row.append('none')
        if student in friendDict:
            if 'not registered' in friendDict[student][2]:
                row.append('<span style="color:green">%s</span>' % friendDict[student][2])
            else:
                row.append('<span style="color:red">%s</span>' % friendDict[student][2])
        table.append(row)
    html = tabulate(table[1:], headers=table[0], tablefmt='html')
    return html


def generateStudentTable(hostHome, dest='html'):
    students = hostHome.student_set.all()
    table = [['Name', 'Grade', 'Phone', 'T Shirt', 'Allergies', 'Parent Phone', 'Parent Email']]
    for student in students:
        row = []
        if dest == 'html':
            studentHref = '<a href="%s">%s %s</a>' % (reverse('student', args=[student.id]), student.firstName, student.lastName)
            row.append(studentHref)
        else:
            row.append('%s %s' % (student.firstName, student.lastName))
        row.append(student.grade)
        row.append(student.phone)
        row.append(student.tshirtSize)
        row.append(student.allergy)
        row.append(student.parentPhone)
        if dest == 'html':
            emailHref = '<a href="mailto:%s">%s</a>' % (student.parentEmail, student.parentEmail)
            row.append(emailHref)
        else:
            row.append('mailto:' + student.parentEmail)
        table.append(row)
    return table


def generateStudentHtml(hostHome, dest='html'):
    data = generateStudentTable(hostHome, dest=dest)
    html = tabulate(data[1:], headers=data[0], tablefmt='html')
    text = tabulate(data[1:], headers=data[0], tablefmt='grid')
    return html, text


def generateCooksTable(hostHome, dest='html'):
    meals = hostHome.meal_set.all().order_by('time')
    table = [['Meal', 'Name', 'Phone', 'Email']]
    for meal in meals:
        row = [meal.time]
        row.append('%s %s' % (meal.cook.firstName, meal.cook.lastName))
        row.append(meal.cook.phone)
        if dest == 'html':
            emailHref = '<a href="mailto:%s">%s</a>' % (meal.cook.email, meal.cook.email)
            row.append(emailHref)
        else:
            row.append(meal.cook.email)
        table.append(row)
    return table


def generateCooksHtml(hostHome, dest='html'):
    data = generateCooksTable(hostHome, dest=dest)
    html = tabulate(data[1:], headers=data[0], tablefmt='html')
    text = tabulate(data[1:], headers=data[0], tablefmt='grid')
    allAllergies = genAllergySummaryString(hostHome)
    html += '<p><span style="background-color: #FFFF00"><b>Allergies: </b> %s</span></p>' % allAllergies
    text += '\nAllergies: %s' % allAllergies
    s = hostHome.student_set.count()
    l = hostHome.leader_set.count()
    html += '<p><b>Number of people to prepare for:</b> %d students, %d leaders plus the host home = ' % (s, l)
    html += '<span style="background-color: #FFFF00">%d people</span></p>' % (s + l + 2)
    text += '\n\nNumber of people to prepare for: %d students, %d leaders plus the host home = %d people' % (s, l, s+l+2 )
    return html, text


def generateDriverDetailsHtml(hostHome, dest='html'):
    data = generateDriverDetailsTable(hostHome, dest=dest)
    if dest == 'email':
        dest = 'html'
    driverHtml = tabulate(data[1:], headers=data[0], tablefmt=dest)
    data = generateDriverDetailsTable(hostHome, dest='text')
    driverText = tabulate(data[1:], headers=data[0], tablefmt='grid')
    return driverHtml, driverText


def generateDriverDetailsTable(hostHome, dest='html'):
    driveSlots = hostHome.driveslot_set.all().order_by('time')
    students = hostHome.student_set.all()
    numStudents = len(students)
    numPassengerLeaders = hostHome.leader_set.exclude(isDriving=True).count()
    slot = 1
    driverTable = [['Time', 'Drivers', 'Summary']]
    if dest == 'html' or dest == 'email':
        newLine = '<br>'
    else:
        newLine = '\n'
    for ds in driveSlots:
        row = []
        # time = ds.time[2:]
        # ds.drivers.objects.aggregate(Sum('carCapacity'))
        totalSeats = 0
        drivers = ds.drivers.all()
        row.append(ds.time)
        cell = ''
        for driver in drivers:
            cell += '%s %s, %s, %d seats%s' % (driver.firstName, driver.lastName, driver.phone, driver.carCapacity, newLine)
            totalSeats += driver.carCapacity
        row.append(cell)

        cell = ''
        cell += '%d drivers : %d seats%s' % (len(drivers), totalSeats, newLine)
        # Student leaders have to be passengers
        # However, they should be able to drive Friday night and Sunday morning
        if slot == 1 or slot == 6:
            numPassengers = numStudents
            cell += '%d students + 0 leaders = %d%s' % (numStudents,  numPassengers, newLine)
        else:
            numPassengers = numStudents + numPassengerLeaders
            cell += '%d students + %d leaders = %d%s' % (numStudents, numPassengerLeaders, numPassengers, newLine)
        seatNeed = getSeatDiff(numPassengers, totalSeats, dest=dest)
        cell += 'Seat need = %s%s' % (seatNeed, newLine)
        slot += 1
        row.append(cell)
        driverTable.append(row)
    return driverTable


def generateOverallSummaryHtml():
    hostHomesList = HostHome.objects.exclude(grade__contains='?').order_by('lastName')
    html = '<table sumary="Host Home Summary Table">'
    html += '<tr>'
    html += '<th>Host</th>'
    html += '<th>Grade</th>'
    html += '<th>Gender</th>'
    html += '<th># Students</th>'
    html += '<th># Leaders</th>'
    for ds in DRIVE_SLOTS:
        time = ds[1][2:]
        html += '<th>%s</th>' % time
    html += '</tr>'
    totStudents = totLeaders = 0
    seats = defaultdict(lambda: 0)
    # need = defaultdict(lambda: 0)
    tshirtCounts = defaultdict(lambda: 0)
    for hh in hostHomesList:
        numStudents = hh.student_set.count()
        totStudents += numStudents
        numLeaders = hh.leader_set.count()
        totLeaders += numLeaders
        numPassengerLeaders = hh.leader_set.exclude(isDriving=True).count()
        # numDrivingLeaders = hh.leader_set.exclude(isDriving=False).count()
        # print('%s Num leaders = %d  driving = %d  not driving = %d' %
        # (hh.lastName, numLeaders, numDrivingLeaders, numPassengerLeaders))
        html += '<tr>'
        html += '<td><a href="/dnow/hosthomes/%s">%s</a></td>' % (hh.id, hh.lastName)
        html += '<td>%s</td>' % hh.grade
        html += '<td>%s</td>' % hh.gender
        html += '<td>%d</td>' % numStudents
        html += '<td>%d</td>' % numLeaders
        slot = 1
        for ds in hh.driveslot_set.all().order_by('time'):
            if hh.grade == '?':
                html += '<td></td>'
            else:
                numSeats = ds.drivers.aggregate(Sum('carCapacity'))
                if numSeats['carCapacity__sum']:
                    totNumSeats = numSeats['carCapacity__sum']
                else:
                    totNumSeats = 0
                # Student leaders have to be passengers
                # However, they should be able to drive Friday night and Sunday morning
                if slot == 1 or slot == 6:
                    numPassengers = numStudents
                else:
                    numPassengers = numStudents + numPassengerLeaders
                seatNeed = getSeatDiff(numPassengers, totNumSeats)
                html += '<td>%d seats, %s</td>' % (totNumSeats, seatNeed)
                seats[ds.time] += totNumSeats
            slot += 1
        html += '</tr>'
        tshirtCounts = countShirts(tshirtCounts, hh)

    html += '<tr>'
    html += '<td>Total</td>'
    html += '<td></td>'
    html += '<td></td>'
    html += '<td>%d</td>' % totStudents
    html += '<td>%d</td>' % totLeaders
    for ds in DRIVE_SLOTS:
        html += '<td>%d seats</td>' % seats[ds[1]]
    html += '</table>'
    html += '<h2>T Shirt Counts</h2>'
    html += generateShirtSizesSummaryHtml(tshirtCounts)

    return html


def getSeatDiff(numStudents, totalSeats, dest='html'):
    seatDiff = totalSeats - numStudents
    if seatDiff == '0':
        seatNeed = 'none'
    elif seatDiff < 0:
        if dest == 'html' or dest == 'email':
            seatNeed = '<span style="color:red">%d short</span>' % abs(seatDiff)
        else:
            seatNeed = '%d short' % abs(seatDiff)
    else:
        if dest == 'html' or dest == 'email':
            seatNeed = '<span style="color:green">%d extra</span>' % seatDiff
        else:
            seatNeed = '%d extra' % seatDiff
    return seatNeed


def countShirts(tsc, hostHome):
    ts = Tshirts(hostHome)
    ts.countShirts()
    for size in SHIRT_SIZES:
        num = ts.tshirtCounts[size[1]]
        tsc[size[1]] += num
    return tsc


def generateHostHomeHtml(hostHome, driver=False):
    hhBaseHtml = render_to_string('dnow/hostHomeBase.html', {'hostHome': hostHome, 'driver': driver})
    return hhBaseHtml


def generateHostHomeText(hostHome, driver=False):
    hhBaseText = render_to_string('dnow/hostHomeBase.txt', {'hostHome': hostHome, 'driver': driver})
    return hhBaseText


def generateChurchStaffTable(dest='html'):
    staffList = Leader.objects.order_by('lastName').filter(churchStaff=True)
    table = [['Name', 'Phone', 'Email']]
    for leader in staffList:
        row = ['%s %s' % (leader.firstName, leader.lastName)]
        row.append(leader.phone)
        if dest == 'html':
            emailHref = '<a href="mailto:%s">%s</a>' % (leader.email, leader.email)
            row.append(emailHref)
        else:
            row.append(leader.email)
        table.append(row)
    return table


def generateChurchStaffHtml(dest='html'):
    data = generateChurchStaffTable(dest=dest)
    html = tabulate(data[1:], headers=data[0], tablefmt='html')
    text = tabulate(data[1:], headers=data[0], tablefmt='grid')
    return html, text


def generateDriveSlotTable(driver, dest='html'):
    driveSlots = driver.driveslot_set.all().order_by('time')
    table = [['Time', 'Host Home']]
    for ds in driveSlots:
        time = ds.time[2:]
        row = [time]
        if dest == 'html':
            hhHref = '<a href="%s">%s</a>' % (reverse('hosthome', args=[ds.hostHome.id]), ds.hostHome.lastName)
            row.append(hhHref)
        else:
            row.append(ds.hostHome.lastName)
        table.append(row)
    return(table)


def generateDriveSlotHtml(driver, dest='html'):
    data = generateDriveSlotTable(driver, dest=dest)
    html = tabulate(data[1:], headers=data[0], tablefmt='html')
    text = tabulate(data[1:], headers=data[0], tablefmt='grid')
    return html, text

def parseObjAllergy(obj):
    allergy = set()
    if obj.allergy:
        if ',' in obj.allergy:
            all = obj.allergy.split(',')
            for a in all:
                allergy.add(a.strip())
        else:
            allergy.add(obj.allergy.strip())
    return allergy


def genAllergySummaryString(hostHome):
    allergies = parseObjAllergy(hostHome)
    for ldr in hostHome.leader_set.all():
        allergy = parseObjAllergy(ldr)
        if allergy:
            # print(ldr.lastName, allergy)
            allergies |= allergy
    for student in hostHome.student_set.all():
        allergy = parseObjAllergy(student)
        if allergy:
            # print(student.lastName, allergy)
            allergies |= allergy

    return ', '.join(allergies)


class HostHomeData(object):
    def __init__(self, hh, dest='html'):
        self.hh = hh
        self.dest = dest
        self.gender = None
        self.baseHtml = self.baseText = None
        self.studentHtml = self.studentText = None
        self.cooksHtml = self.cooksText = None
        self.leaderHtml = self.leaderText = None
        self.driverHtml = self.driverText = None
        self.tshirtHtml = self.tshirtText = None
        self.churchStaffHtml = self.churchStaffText = None
        self.prevIndx = 0
        self.nextIndx = 0
        self.studentCount = 0
        self.leaderCount = 0
        self.hostHomeIdList = []
        self.hostHomeIdList = []
        self.context = None
        self.genAllData()

    def genAllData(self):
        self.genHostHomeBasics()
        self.genChurchStaffData()
        self.genCookData()
        self.genDriverData()
        self.genLeaderData()
        self.genStudentData()
        self.genPrevNextHtmlIndices()
        self.genTshirtData()
        self.getGender()

    def genHostHomeBasics(self):
        self.baseHtml = generateHostHomeHtml(self.hh)
        self.baseText = generateHostHomeText(self.hh)

    def genPrevNextHtmlIndices(self):
        # hostHomeList = HostHome.objects.order_by('lastName')
        hostHomeList = HostHome.objects.exclude(grade__contains='?').order_by('lastName')
        self.hostHomeIdList, self.prevIndx, self.nextIndx = genPrevNextFromIdList(hostHomeList, self.hh.id)

    def genStudentData(self):
        self.studentCount = self.hh.student_set.count()
        self.studentHtml, self.studentText = generateStudentHtml(self.hh, dest=self.dest)

    def genCookData(self):
        self.cooksHtml, self.cooksText = generateCooksHtml(self.hh, dest=self.dest)

    def genLeaderData(self):
        self.leaderCount = self.hh.leader_set.count()
        self.leaderHtml, self.leaderText = generateLeadersHtml(self.hh)

    def genDriverData(self):
        self.driverHtml, self.driverText = generateDriverDetailsHtml(self.hh, dest=self.dest)

    def genTshirtData(self):
        self.tshirtHtml, self.tshirtText = generateShirtSizesHtml(self.hh)

    def genChurchStaffData(self):
        self.churchStaffHtml, self.churchStaffText = generateChurchStaffHtml(dest=self.dest)

    def getGender(self):
        if self.hh.gender == 'F':
            self.gender = 'girls'
        else:
            self.gender = 'boys'

    def getHtmlContext(self):
        context = {
            'hostHome': self.hh,
            'gender': self.gender,
            'hhBaseHtml': self.baseHtml,
            'studentCount': self.hh.student_set.count(),
            'leaderCount': self.hh.leader_set.count(),
            'studentHtml': self.studentHtml,
            'cooksHtml': self.cooksHtml,
            'leaderHtml': self.leaderHtml,
            'driverHtml': self.driverHtml,
            'tshirtHtml': self.tshirtHtml,
            'churchStaffHtml': self.churchStaffHtml,
            'next': self.hostHomeIdList[self.nextIndx],
            'prev': self.hostHomeIdList[self.prevIndx]
        }
        return context

    def getTextContext(self):
        context = {
            'hostHome': self.hh,
            'gender': self.gender,
            'hhBaseHtml': self.baseText,
            'studentCount': self.hh.student_set.count(),
            'leaderCount': self.hh.leader_set.count(),
            'studentHtml': self.studentText,
            'cooksHtml': self.cooksText,
            'leaderHtml': self.leaderText,
            'driverHtml': self.driverText,
            'tshirtHtml': self.tshirtText,
            'churchStaffHtml': self.churchStaffText,
            'next': self.hostHomeIdList[self.nextIndx],
            'prev': self.hostHomeIdList[self.prevIndx]
        }
        return context


def genPrevNextFromIdList(objList, id):
    idList = list(objList.values_list('id', flat=True))
    indx = idList.index(id)
    nextIndx = indx + 1
    prevIndx = indx - 1
    if prevIndx < 0:
        prevIndx = len(idList)-1
    if nextIndx > len(idList)-1:
        nextIndx = 0
    return idList, prevIndx, nextIndx
