from collections import defaultdict

from django.db.models import Sum

from dnow.models import *
from django.db.models import Sum


def generateDriverDetailsHtml(hostHome):
    driveSlots = hostHome.driveslot_set.all().order_by('time')
    students = hostHome.student_set.all()
    html = '<table sumary="Driver Table">'
    html += '<tr>'
    html += '<th>Time</th>'
    html += '<th>Drivers</th>'
    html += '<th>Summary</th>'
    html += '</tr>'
    for ds in driveSlots:
        time = ds.time[2:]
        # ds.drivers.objects.aggregate(Sum('carCapacity'))
        totalSeats = 0
        drivers = ds.drivers.all()
        html += '<tr>'
        html += '<td><b>%s</b></td>' % time
        html += '<td><ul>'
        for driver in drivers:
            html += '<li>%s %s, %s %d seats</li>' % (driver.firstName, driver.lastName, driver.phone, driver.carCapacity)
            totalSeats += driver.carCapacity
        html += '</ul></td>'

        numStudents = len(students)
        seatNeed = getSeatDiff(numStudents, totalSeats)
        html += '<td>'
        html += '%d drivers<br>' % len(drivers)
        html += '%d seats<br>' % totalSeats
        html += '%d students<br>' % numStudents
        html += 'Seat need = %s' % seatNeed
        html += '</td></tr>'
    html += '</table>'
    return(html)

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
    need = defaultdict(lambda: 0)
    for hh in hostHomesList:
        numStudents = hh.student_set.count()
        totStudents += numStudents
        numLeaders = hh.leader_set.count()
        totLeaders += numLeaders
        html += '<tr>'
        html += '<td><a href="/dnow/hosthomes/%s">%s</a></td>' % (hh.id, hh.lastName)
        html += '<td>%s</td>' % hh.grade
        html += '<td>%s</td>' % hh.gender
        html += '<td>%d</td>' % numStudents
        html += '<td>%d</td>' % numLeaders
        for ds in hh.driveslot_set.all().order_by('time'):
            if hh.grade == '?':
                html += '<td></td>'
            else:
                numSeats = ds.drivers.aggregate(Sum('carCapacity'))
                if numSeats['carCapacity__sum']:
                    totNumSeats = numSeats['carCapacity__sum']
                else:
                    totNumSeats = 0
                seatNeed = getSeatDiff(numStudents, totNumSeats)
                html += '<td>%d seats, need = %s</td>' % (totNumSeats, seatNeed)
                seats[ds.time] += totNumSeats
        html += '</tr>'
    html += '<tr>'
    html += '<td>Total</td>'
    html += '<td></td>'
    html += '<td></td>'
    html += '<td>%d</td>' % totStudents
    html += '<td>%d</td>' % totLeaders
    for ds in DRIVE_SLOTS:
        html += '<td>%d seats</td>' % seats[ds[1]]
    html += '</table>'
    return(html)

def getSeatDiff(numStudents, totalSeats):
    seatDiff = totalSeats - numStudents
    if seatDiff == '0':
        seatNeed = 'none'
    elif seatDiff < 0:
        seatNeed = '<span style="color:red">%d short</span>' % abs(seatDiff)
    else:
        seatNeed = '<span style="color:green">%d extra</span>' % seatDiff
    return seatNeed
