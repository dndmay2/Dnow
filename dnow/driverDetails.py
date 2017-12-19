from collections import defaultdict

from django.db.models import Sum

from dnow.models import *
from django.db.models import Sum
from shirtSizes import Tshirts


def generateDriverDetailsHtml(hostHome):
    driveSlots = hostHome.driveslot_set.all().order_by('time')
    students = hostHome.student_set.all()
    numStudents = len(students)
    numPassengerLeaders = hostHome.leader_set.exclude(isDriving=True).count()
    html = '<table sumary="Driver Table">'
    html += '<tr>'
    html += '<th>Time</th>'
    html += '<th>Drivers</th>'
    html += '<th>Summary</th>'
    html += '</tr>'
    slot = 1
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

        html += '<td>'
        html += '%d drivers : %d seats<br>' % (len(drivers), totalSeats)
        # Student leaders have to be passengers
        # However, they should be able to drive Friday night and Sunday morning
        if slot == 1 or slot == 6:
            numPassengers = numStudents
            html += '%d students + 0 leaders = %d<br>' % (numStudents,  numPassengers)
        else:
            numPassengers = numStudents + numPassengerLeaders
            html += '%d students + %d leaders = %d<br>' % (numStudents, numPassengerLeaders, numPassengers)
        seatNeed = getSeatDiff(numPassengers, totalSeats)
        html += 'Seat need = %s' % seatNeed
        html += '</td></tr>'
        slot += 1
    html += '</table>'
    ts = Tshirts(hostHome)
    ts.countShirts()
    html += ts.createTshirtHtml()
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
    tshirtCounts = defaultdict(lambda: 0)
    for hh in hostHomesList:
        numStudents = hh.student_set.count()
        totStudents += numStudents
        numLeaders = hh.leader_set.count()
        totLeaders += numLeaders
        numPassengerLeaders = hh.leader_set.exclude(isDriving=True).count()
        # numDrivingLeaders = hh.leader_set.exclude(isDriving=False).count()
        # print('%s Num leaders = %d  driving = %d  not driving = %d' % (hh.lastName, numLeaders, numDrivingLeaders, numPassengerLeaders))
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
    print(tshirtCounts)
    ts = Tshirts(None)
    ts.tshirtCounts = tshirtCounts
    html += ts.createTshirtHtml()

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

def countShirts(tsc, hostHome):
    ts = Tshirts(hostHome)
    ts.countShirts()
    for size in SHIRT_SIZES:
        num = ts.tshirtCounts[size[1]]
        tsc[size[1]] += num
    return tsc
