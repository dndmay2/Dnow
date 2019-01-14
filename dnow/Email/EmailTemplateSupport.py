from dnow.models import *
from dnow.htmlGenerators import *
from dnow.forms import HostHomeDropDownForm, LeaderDropDownForm, StudentDropDownForm, DriverDropDownForm, \
    CookDropDownForm


def filterTheContext(context, template):
    if 'hostHomeBasics' not in template.includeData:
        context['hhBaseHtml'] = None
    if 'churchStaff' not in template.includeData:
        context['churchStaffHtml'] = None
    if 'cooks' not in template.includeData:
        context['cooksHtml'] = None
    if 'driverData' not in template.includeData:
        context['driverHtml'] = None
    if 'leaders' not in template.includeData:
        context['leaderHtml'] = None
    if 'students' not in template.includeData:
        context['studentHtml'] = None
    if 'tshirts' not in template.includeData:
        context['tshirtHtml'] = None
    return context

def getCurrentObject(template, request):
    if template.toGroups == 'hostHomes':
        curObject, hhData, form, sendAll = getHostHomeFromHostHomeDropdown(request)
        objects = HostHome.objects.filter(user=request.user)
    elif template.toGroups == 'drivers':
        curObject, hhData, form, sendAll = getDriverFromDriverDropdown(request)
        objects = Driver.objects.filter(user=request.user)
    elif template.toGroups == 'leaders':
        curObject, hhData, form, sendAll = getLeaderFromLeaderDropdown(request)
        objects = Leader.objects.filter(user=request.user)
    elif template.toGroups == 'parents':
        curObject, hhData, form, sendAll = getStudentFromStudentDropdown(request)
        objects = Student.objects.filter(user=request.user)
    elif template.toGroups == 'cooks':
        curObject, hhData, form, sendAll = getCookFromCookDropdown(request)
        objects = Cook.objects.filter(user=request.user)
    else:
        curObject = hhData = form = sendAll = objects = None
    return curObject, hhData, form, sendAll, objects


def getHostHomeFromObject(object):
    if object.__class__.__name__ == 'HostHome':
        return object
    elif object.__class__.__name__ == 'Student':
        return object.hostHome
    else:
        return None

def getEmailForObject(object):
    if object.__class__.__name__ == 'Student':
        return object.parentEmail
    else:
        return object.email

def getHostHomeFromHostHomeDropdown(request):
    sendAll = False
    objExample = HostHome.objects.filter(user=request.user).first()
    if request.GET:
        form = HostHomeDropDownForm(request.user, request.GET)
        # print('errors', form.errors)
        if form.is_valid():
            selectedObject = form.cleaned_data['hostHomes']
            # print('YO', selectedObject)
            if selectedObject:
                objExample = selectedObject
                sendAll = False
            else:
                sendAll = True
    else:
        form = HostHomeDropDownForm(request.user)
        sendAll = True
    hhData = HostHomeData(objExample, user=request.user, dest='email')
    return objExample, hhData, form, sendAll


def getLeaderFromLeaderDropdown(request):
    sendAll = False
    objExample = Leader.objects.filter(user=request.user).first()
    if request.GET:
        form = LeaderDropDownForm(request.user, request.GET)
        # print('errors', form.errors)
        if form.is_valid():
            selectedObject = form.cleaned_data['leaders']
            # print('YO', selectedObject)
            if selectedObject:
                objExample = selectedObject
                sendAll = False
            else:
                sendAll = True
    else:
        form = LeaderDropDownForm(request.user)
        sendAll = True
    hhData = HostHomeData(objExample.hostHome, user=request.user, dest='email')
    return objExample, hhData, form, sendAll


def getStudentFromStudentDropdown(request):
    sendAll = False
    objExample = Student.objects.filter(user=request.user).first()
    if request.GET:
        form = StudentDropDownForm(request.user, request.GET)
        # print('errors', form.errors)
        if form.is_valid():
            selectedObject = form.cleaned_data['students']
            # print('YO', selectedObject)
            if selectedObject:
                objExample = selectedObject
                sendAll = False
            else:
                sendAll = True
    else:
        form = StudentDropDownForm(request.user)
        sendAll = True
    hhData = HostHomeData(objExample.hostHome, user=request.user, dest='email')
    return objExample, hhData, form, sendAll

def getDriverFromDriverDropdown(request):
    sendAll = False
    objExample = Driver.objects.filter(user=request.user).first()
    if request.GET:
        form = DriverDropDownForm(request.user, request.GET)
        # print('errors', form.errors)
        if form.is_valid():
            selectedObject = form.cleaned_data['drivers']
            # print('YO', selectedObject)
            if selectedObject:
                objExample = selectedObject
                sendAll = False
            else:
                sendAll = True
    else:
        form = DriverDropDownForm(request.user)
        sendAll = True
    # hhData = HostHomeData(objExample.hostHome, user=request.user, dest='email')
    hhData = None
    return objExample, hhData, form, sendAll

def getCookFromCookDropdown(request):
    sendAll = False
    objExample = Cook.objects.filter(user=request.user).first()
    if request.GET:
        form = CookDropDownForm(request.user, request.GET)
        # print('errors', form.errors)
        if form.is_valid():
            selectedObject = form.cleaned_data['cooks']
            # print('YO', selectedObject)
            if selectedObject:
                objExample = selectedObject
                sendAll = False
            else:
                sendAll = True
    else:
        form = CookDropDownForm(request.user)
        sendAll = True
    # hhData = HostHomeData(objExample.hostHome, user=request.user, dest='email')
    hhData = None
    return objExample, hhData, form, sendAll

def getCookContext(user, cook):
    churchStaffHtml, churchStaffText = generateChurchStaffHtml(user, dest='email')
    hostHomes = {meal.hostHome for meal in cook.meal_set.all()}
    hhHtml = ''
    hhText = ''
    for hh in hostHomes:
        hhHtml += generateHostHomeHtml(hh, driver=True)
        hhText += generateHostHomeText(hh, driver=True)
        # hhHtml += '<br>'
        # hhText += '\n'
        h, t = generateCooksHtml(hh, dest='email')
        hhHtml += h
        hhText += t

    htmlContext = {
        'cook': cook,
        'hostHomeHtml': hhHtml,
        'churchStaffHtml': churchStaffHtml,
        'isCook': True
    }
    textContext = {
        'cook': cook,
        'hostHomeHtml': hhText,
        'churchStaffHtml': churchStaffText,
        'isCook': True
    }
    return htmlContext, textContext


def getDriverContext(user, driver):
    churchStaffHtml, churchStaffText = generateChurchStaffHtml(user, dest='email')
    driveSlots = driver.driveslot_set.all().order_by('time')
    hostHomes = {ds.hostHome for ds in driveSlots}
    dsHtml, dsText = generateDriveSlotHtml(driver, dest='email')
    hhHtml = ''
    hhText = ''
    for hh in hostHomes:
        hhHtml += generateHostHomeHtml(hh, driver=True)
        hhText += generateHostHomeText(hh, driver=True)

    htmlContext = {
        'driver': driver,
        'driveSlots': dsHtml,
        'hostHomeHtml': hhHtml,
        'churchStaffHtml': churchStaffHtml,
        'isDriver': True
    }
    textContext = {
        'driver': driver,
        'driveSlots': dsText,
        'hostHomeHtml': hhText,
        'churchStaffHtml': churchStaffText,
        'isDriver': True
    }
    return htmlContext, textContext
