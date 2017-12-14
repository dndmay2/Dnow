# Create your views here.
from django.shortcuts import get_object_or_404, render

from Spreadsheet.ReadSpreadsheet import ReadSpreadsheet
from dnow.driverDetails import generateDriverDetailsHtml, generateOverallSummaryHtml
from .models import Student, Parent, HostHome, Driver, Cook, Leader


def index(request):
    parentList = Parent.objects.order_by('lastName')
    studentList = Student.objects.order_by('gender', 'grade', 'lastName')
    context = {
        'studentList': studentList,
        'parentList': parentList,
    }
    print('studentList = %d ' % len(studentList))
    return render(request, 'dnow/index.html', context)


def parent(request, parent_id):
    # type: (object, object) -> object
    p = get_object_or_404(Parent, pk=parent_id)
    return render(request, 'dnow/parent.html', {'parent': p})


def driver(request, driver_id):
    # type: (object, object) -> object
    p = get_object_or_404(Driver, pk=driver_id)
    return render(request, 'dnow/driver.html', {'driver': p})


def cook(request, cook_id):
    # type: (object, object) -> object
    p = get_object_or_404(Cook, pk=cook_id)
    return render(request, 'dnow/cook.html', {'cook': p})


def leader(request, leader_id):
    # type: (object, object) -> object
    p = get_object_or_404(Leader, pk=leader_id)
    return render(request, 'dnow/leader.html', {'leader': p})


def student(request, student_id):
    # type: (object, object) -> object
    s = get_object_or_404(Student, pk=student_id)
    studentList = Student.objects.order_by('gender', 'grade', 'lastName')
    studentIdList = list(studentList.values_list('id', flat=True))
    sIndx = studentIdList.index(s.id)
    nextIndx = sIndx + 1
    prevIndx = sIndx - 1
    if prevIndx < 0:
        prevIndx = len(studentIdList)-1
    if nextIndx > len(studentIdList)-1:
        nextIndx = 0

    context = {
        'student': s,
        'next': studentIdList[nextIndx],
        'prev': studentIdList[prevIndx]
    }
    return render(request, 'dnow/student.html', context)


def hosthome(request, hosthome_id):
    # type: (object, object) -> object
    hh = get_object_or_404(HostHome, pk=hosthome_id)
    hostHomeList = HostHome.objects.order_by('lastName')
    hostHomeIdList = list(hostHomeList.values_list('id', flat=True))
    hhIndx = hostHomeIdList.index(hh.id)
    nextIndx = hhIndx + 1
    prevIndx = hhIndx - 1
    if prevIndx < 0:
        prevIndx = len(hostHomeIdList)-1
    if nextIndx > len(hostHomeIdList)-1:
        nextIndx = 0
    students = hh.student_set.all()
    leaders = hh.leader_set.all()
    meals = hh.meal_set.all().order_by('time')
    driveSlots = hh.driveslot_set.all().order_by('time')
    driverHtml = generateDriverDetailsHtml(hh)

    context = {
        'hosthome': hh,
        'studentList': students,
        'leaderList': leaders,
        'mealList': meals,
        'driveSlotList': driveSlots,
        'driverHtml': driverHtml,
        'next': hostHomeIdList[nextIndx],
        'prev': hostHomeIdList[prevIndx]
    }
    return render(request, 'dnow/hosthome.html', context)


def spreadsheet(request):
    if request.GET.get('readSpreadsheet'):
        ss = ReadSpreadsheet()
        ss.readHosts()
        ss.readStudents()
        ss.readCooks()
        ss.readLeaders()
        ss.readDrivers()
    return render(request, 'dnow/spreadsheet.html')


def all_hosthomes(request):
    hostHomeSummary = generateOverallSummaryHtml()
    context = {
        'hostHomeSummary': hostHomeSummary,
    }
    return render(request, 'dnow/all_hosthomes.html', context)


def all_drivers(request):
    driversList = Driver.objects.order_by('lastName')
    seatCount = 0
    for driver in driversList:
        seatCount = seatCount + driver.carCapacity
    context = {
        'driversList': driversList,
        'seatCount': seatCount,
    }
    return render(request, 'dnow/all_drivers.html', context)


def all_cooks(request):
    cooksList = Cook.objects.order_by('lastName')
    context = {
        'cooksList': cooksList,
    }
    return render(request, 'dnow/all_cooks.html', context)


def all_leaders(request):
    leadersList = Leader.objects.order_by('lastName')
    context = {
        'leadersList': leadersList,
    }
    return render(request, 'dnow/all_leaders.html', context)
