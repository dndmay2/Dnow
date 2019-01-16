# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.core.mail import mail_admins
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy

from Spreadsheet.ReadSpreadsheet import ReadSpreadsheet, checkStudentFriendMatchups
from dnow.Email.EmailTemplateSupport import *
from dnow.Email.SendEmail import *
from dnow.htmlGenerators import *
from .models import Student, Parent, HostHome, Driver, Cook, Leader, Profile, EmailTemplate
from .forms import SettingForm, EmailTemplateForm, HostHomeDropDownForm, LeaderDropDownForm, StudentDropDownForm

import config
import time


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
                    Profile.objects.create(user=user, googleSpreadSheet='googleSpreadSheet', churchName='campus', churchEmailAddress='me@gmail.com')
                    print('failed if')
                    Profile.objects.create(user=user, googleSpreadSheet='googleSpreadSheet', churchName='campus', churchEmailAddress='me@gmail.com')
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
    password = '#' * len(user.profile.churchEmailPassword)
    print(password)
    return render(request, 'dnow/user_details.html', {'user': user, 'password': password})

# @login_required
def index(request):
    user = request.user
    if not user.is_authenticated():
        return redirect('/dnow/login/')
    studentTable = generateAllStudentHtmlTable(user)
    context = {
        'studentTable': studentTable,
    }
    return render(request, 'dnow/index.html', context)


def parent(request, parent_id):
    # type: (object, object) -> object
    p = get_object_or_404(Parent, pk=parent_id)
    return render(request, 'dnow/parent.html', {'parent': p})


@login_required
def driver(request, driver_id):
    # type: (object, object) -> object
    user = request.user
    driver = get_object_or_404(Driver, pk=driver_id)
    dsHtml, dsText = generateDriveSlotHtml(driver, dest='html')
    driverList = Driver.objects.filter(user=user).order_by('lastName')
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


@login_required
def cook(request, cook_id):
    # type: (object, object) -> object
    p = get_object_or_404(Cook, pk=cook_id)
    return render(request, 'dnow/cook.html', {'cook': p})


@login_required
def leader(request, leader_id):
    # type: (object, object) -> object
    user = request.user
    leader = get_object_or_404(Leader, pk=leader_id)
    leaderList = Leader.objects.filter(user=user).order_by('lastName')
    idList, prevIndx, nextIndx = genPrevNextFromIdList(leaderList, leader.id)
    context = {
        'leader': leader,
        'next': idList[nextIndx],
        'prev': idList[prevIndx]
    }
    return render(request, 'dnow/leader.html', context)


@login_required
def student(request, student_id):
    # type: (object, object) -> object
    user = request.user
    s = get_object_or_404(Student, pk=student_id)
    studentList = Student.objects.filter(user=user).filter(user=user).order_by('gender', 'grade', 'lastName')
    studentIdList, prevIndx, nextIndx = genPrevNextFromIdList(studentList, s.id)

    context = {
        'student': s,
        'next': studentIdList[nextIndx],
        'prev': studentIdList[prevIndx]
    }
    return render(request, 'dnow/student.html', context)


@login_required
def hosthome(request, hosthome_id):
    # type: (object, object) -> object
    hh = get_object_or_404(HostHome, pk=hosthome_id)
    hhData = HostHomeData(hh, user=request.user, dest='html')
    context = hhData.getHtmlContext()
    return render(request, 'dnow/hosthome.html', context)


@login_required
def all_hosthomes(request):
    hostHomeSummary = generateOverallSummaryHtml(request.user)
    context = {
        'hostHomeSummary': hostHomeSummary,
    }
    return render(request, 'dnow/all_hosthomes.html', context)


@login_required
def all_drivers(request):
    user = request.user
    driversList = Driver.objects.filter(user=user).order_by('lastName')
    seatCount = 0
    for d in driversList:
        seatCount = seatCount + d.carCapacity
    context = {
        'driversList': driversList,
        'seatCount': seatCount,
    }
    return render(request, 'dnow/all_drivers.html', context)


@login_required
def all_cooks(request):
    user = request.user
    cooksList = Cook.objects.filter(user=user).order_by('lastName')
    context = {
        'cooksList': cooksList,
    }
    return render(request, 'dnow/all_cooks.html', context)


@login_required
def all_leaders(request):
    user = request.user
    leadersList = Leader.objects.filter(user=user).order_by('lastName')
    context = {
        'leadersList': leadersList,
    }
    return render(request, 'dnow/all_leaders.html', context)


@login_required
def spreadsheet(request):
    if request.GET.get('readSpreadsheet'):
        ss = ReadSpreadsheet(request.user)
        ss.readHosts()
        ss.readStudents()
        ss.readCooks()
        ss.readDrivers()
        ss.readLeaders()
        logMessage = 'Done reading spreadsheet!'
    else:
        logMessage = ''
    return render(request, 'dnow/spreadsheet.html', {'logMessage': logMessage})


@login_required
def viewSpreadSheetLog(request):
    context = {
        'log': config.SPREADSHEET_LOG,
    }
    return render(request, 'dnow/spreadsheetLog.html', context)

@login_required
def email(request):
    if request.GET.get('emailHostHomes'):
        print('emailHostHomes was pressed')
        emailAllHostHomes(request.user)
    elif request.GET.get('emailDrivers'):
        print('emailDrivers was pressed')
        emailAllDrivers(request.user)
    return render(request, 'dnow/emailPage.html')

# @login_required
class emailTemplateCreate(CreateView):
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'dnow/emailtemplateCreate.html'
    success_url = reverse_lazy('emailTemplatesViewAll')
    # fields = ('name', 'greeting', 'closing', 'includeData', 'toGroups')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        return super(emailTemplateCreate, self).form_valid(form)

class emailTemplateUpdate(UpdateView):
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'dnow/emailtemplateCreate.html'
    success_url = reverse_lazy('emailTemplatesViewAll')
    # fields = ('name', 'greeting', 'closing', 'includeData', 'toGroups')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        return super(emailTemplateUpdate, self).form_valid(form)

@login_required
def emailTemplatesViewAll(request):
    templates = EmailTemplate.objects.filter(user=request.user).order_by('name')
    return render(request, 'dnow/emailTemplatesViewAll.html', {'templates': templates})

def emailTemplateView(request, template_id):
    # type: (object, object) -> object
    template = get_object_or_404(EmailTemplate, pk=template_id)
    print('template.togroups', template.toGroups)
    sendAll = False
    form = objects = hhData = None
    curObject, hhData, form, sendAll, objects = getCurrentObject(template, request)
    hh = getHostHomeFromObject(curObject)
    context = {}
    if hhData:
        context = hhData.getHtmlContext()
        context = filterTheContext(context, template)
        textContext = hhData.getTextContext()
        textContext = filterTheContext(textContext, template)
        context['isCook'] = context['isDriver'] = False
        context['personName'] = getPersonName(curObject)
    else:
        if template.toGroups == 'cooks':
            context, textContext = getCookContext(request.user, curObject)
        elif template.toGroups == 'drivers':
            context, textContext = getDriverContext(request.user, curObject)
        if 'schedule' not in template.includeData:
            context['schedule'] = None
        else:
            context['schedule'] = True

    context['template'] = textContext['template'] = template
    context['hostHome'] = textContext['hostHome'] = hh
    context['curObject'] = textContext['curObject'] = curObject
    context['curEmail'] = textContext['curEmail'] = getEmailForObject(curObject)
    context['sendWaiver'] = checkIfWaiverNeeded(curObject)
    context['objects'] = objects
    context['form'] = form
    context['logMessage'] = ''
    context['htmlGreeting'] = template.greeting.replace('\n', '<br>')
    context['htmlClosing'] = template.closing.replace('\n', '<br>')
    context['sendAll'] = sendAll
    context['scheduleFileName'] = request.user.profile.scheduleFileName

    sendEmail = debug = False
    debugMsg = ''
    if request.GET.get('sendTestEmail'):
        debug = True
        debugMsg = ' (Debug only sent to me)'
        sendEmail = True
    if request.GET.get('sendRealEmail'):
        sendEmail = True
    if sendEmail:
        if sendAll:
            context['logMessage'] = 'Sent all emails%s @ %s' % (debugMsg, time.strftime("%Y-%m-%d %H:%M"))
            context['results'] = dnowEmailAllTest(user=request.user, startingContext=context, debug=debug)
        else:
            context['logMessage'] = 'Sent one email%s @ %s' % (debugMsg, time.strftime("%Y-%m-%d %H:%M"))
            context['results'] = dnowEmailTest(user=request.user, htmlContext=context, textContext=textContext, debug=debug)
        debug = False
    elif request.GET.get('sendRealEmail'):
        context['logMessage'] = 'Sent real email to list'
    return render(request, 'dnow/emailTemplateView.html', context)



def emailTemplateDelete(request, template_id):
    template = get_object_or_404(EmailTemplate, pk=template_id)
    if request.method=='POST':
        template.delete()
        return redirect('/dnow/emailTemplatesViewAll/')
    return render(request, 'dnow/emailTemplateDelete.html', {'object': template})

def sendEmails(request):
    form = HostHomeDropDownForm(request.user)
    if request.GET.get('dnowEmailTest'):
        dnowEmailTest(request.user, debug=True)
    return render(request, 'dnow/sendEmail.html',{'form': form})
