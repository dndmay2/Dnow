# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.core.mail import mail_admins
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required

from Spreadsheet.ReadSpreadsheet import ReadSpreadsheet, checkStudentFriendMatchups
from dnow.Email.SendEmail import *
from dnow.htmlGenerators import *
from .models import Student, Parent, HostHome, Driver, Cook, Leader, Profile
from .forms import SettingForm
import config

def profile(request):
    #...
    pass

@login_required
def settings(request):
    user = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        f = SettingForm(request.POST, instance=user.profile)
        if f.is_valid():
            f.save()
            messages.add_message(request, messages.INFO, 'Settings Saved.')
            return redirect('/dnow/user_details/')

    else:
        f = SettingForm(instance=user.profile)

    return render(request, 'dnow/settings.html', {'form': f})


def login(request):
    if request.user.is_authenticated():
        return redirect('/dnow/user_details/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            # correct username and password login the user
            auth.login(request, user)
            try:
                if hasattr(user, 'profile') and user.profile is not None:
                    print('found profile', user.profile)
                else:
                    Profile.objects.create(user=user, googleSpreadSheet='googleSpreadSheet', church='campus', googleDriveEmail='me@gmail.com')
                    print('failed if')
                    Profile.objects.create(user=user, googleSpreadSheet='googleSpreadSheet', church='campus', googleDriveEmail='me@gmail.com')
            except Exception:
                print('did not find profile')
            return redirect('/dnow/')

        else:
            messages.error(request, 'Error wrong username/password')

    return render(request, 'dnow/login.html')


def logout(request):
    auth.logout(request)
    return render(request,'dnow/logout.html')


def user_details(request):
    user = get_object_or_404(User, id=request.user.id)
    return render(request, 'dnow/user_details.html', {'user': user})


def index(request):
    studentTable = generateAllStudentHtmlTable()
    context = {
        'studentTable': studentTable,
    }
    return render(request, 'dnow/index.html', context)


def parent(request, parent_id):
    # type: (object, object) -> object
    p = get_object_or_404(Parent, pk=parent_id)
    return render(request, 'dnow/parent.html', {'parent': p})


def driver(request, driver_id):
    # type: (object, object) -> object
    driver = get_object_or_404(Driver, pk=driver_id)
    dsHtml, dsText = generateDriveSlotHtml(driver, dest='html')
    driverList = Driver.objects.order_by('lastName')
    idList, prevIndx, nextIndx = genPrevNextFromIdList(driverList, driver.id)
    hostHomes = { ds.hostHome for ds in driver.driveslot_set.all() }
    hhHtml = ''
    for hh in hostHomes:
        hhHtml += generateHostHomeHtml(hh, driver=True)
    context  = {
        'driver': driver,
        'driveSlotsHtml': dsHtml,
        'hostHomeHtml': hhHtml,
        'next': idList[nextIndx],
        'prev': idList[prevIndx]
    }
    return render(request, 'dnow/driver.html', context)


def cook(request, cook_id):
    # type: (object, object) -> object
    p = get_object_or_404(Cook, pk=cook_id)
    return render(request, 'dnow/cook.html', {'cook': p})


def leader(request, leader_id):
    # type: (object, object) -> object
    leader = get_object_or_404(Leader, pk=leader_id)
    leaderList = Leader.objects.order_by('lastName')
    idList, prevIndx, nextIndx = genPrevNextFromIdList(leaderList, leader.id)
    context = {
        'leader': leader,
        'next': idList[nextIndx],
        'prev': idList[prevIndx]
    }
    return render(request, 'dnow/leader.html', context)


def student(request, student_id):
    # type: (object, object) -> object
    s = get_object_or_404(Student, pk=student_id)
    studentList = Student.objects.order_by('gender', 'grade', 'lastName')
    studentIdList, prevIndx, nextIndx = genPrevNextFromIdList(studentList, s.id)

    context = {
        'student': s,
        'next': studentIdList[nextIndx],
        'prev': studentIdList[prevIndx]
    }
    return render(request, 'dnow/student.html', context)


def hosthome(request, hosthome_id):
    # type: (object, object) -> object
    hh = get_object_or_404(HostHome, pk=hosthome_id)
    hhData = HostHomeData(hh, dest='html')
    context = hhData.getHtmlContext()
    return render(request, 'dnow/hosthome.html', context)


def all_hosthomes(request):
    hostHomeSummary = generateOverallSummaryHtml()
    context = {
        'hostHomeSummary': hostHomeSummary,
    }
    return render(request, 'dnow/all_hosthomes.html', context)


def all_drivers(request):
    driversList = Driver.objects.order_by('lastName')
    seatCount = 0
    for d in driversList:
        seatCount = seatCount + d.carCapacity
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


def spreadsheet(request):
    if request.GET.get('readSpreadsheet'):
        ss = ReadSpreadsheet(request.user)
        ss.readHosts()
        ss.readStudents()
        ss.readCooks()
        ss.readDrivers()
        ss.readLeaders()
    return render(request, 'dnow/spreadsheet.html')


def viewSpreadSheetLog(request):
    context = {
        'log': config.SPREADSHEET_LOG,
    }
    return render(request, 'dnow/spreadsheetLog.html', context)

def email(request):
    if request.GET.get('emailHostHomes'):
        print('emailHostHomes was pressed')
        emailAllHostHomes()
    elif request.GET.get('emailDrivers'):
        print('emailDrivers was pressed')
        emailAllDrivers()
    return render(request, 'dnow/emailPage.html')
