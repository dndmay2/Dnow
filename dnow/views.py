# Create your views here.
from django.shortcuts import get_object_or_404, render

from Spreadsheet.ReadSpreadsheet import ReadSpreadsheet
from .models import Student, Parent, HostHome, Driver, Cook


def index(request):
    parentList = Parent.objects.order_by('lastName')
    studentList = Student.objects.order_by('lastName')
    context = {
        'studentList': studentList,
        'parentList': parentList,
    }
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


def student(request, student_id):
    # type: (object, object) -> object
    s = get_object_or_404(Student, pk=student_id)
    studentList = Student.objects.order_by('lastName')
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
    return render(request, 'dnow/hosthome.html', {'hosthome': hh})


def spreadsheet(request):
    if request.GET.get('readSpreadsheet'):
        ss = ReadSpreadsheet()
        ss.readStudents()
        ss.readHosts()
        ss.readCooks()
    return render(request, 'dnow/spreadsheet.html')


def all_hosthomes(request):
    hostHomesList = HostHome.objects.order_by('lastName')
    context = {
        'hostHomesList': hostHomesList,
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
