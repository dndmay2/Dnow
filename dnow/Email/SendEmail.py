import os

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives, get_connection

from dnow.htmlGenerators import *
from dnow.models import *


def dnowEmailTest(debug=True):
    # hh = HostHome.objects.get(lastName='May')
    # emailHostHome(hh, debug=debug)
    # driver = Driver.objects.get(lastName='May', firstName='Derek')
    # emailDriver(driver, debug=debug)
    # cook = Cook.objects.get(lastName='Lasseter', firstName='Katie')
    # emailCook(cook, debug=debug)
    student = Student.objects.get(lastName='May', firstName='Avery')
    student = Student.objects.get(lastName='Weeks', firstName='Annabelle')
    emailParent(student, debug=debug)


def emailHostHome(hh, debug=False):
    hhData = HostHomeData(hh, dest='email')
    htmlContext = hhData.getHtmlContext()
    textContext = hhData.getTextContext()
    msgPlain = render_to_string('dnow/emailHostHomes.txt', context=textContext)
    msgHtml = render_to_string('dnow/emailHostHomes.html', context=htmlContext)

    leaderEmails = [ leader.email for leader in hh.leader_set.all() ]
    toList = [ hh.email ] + leaderEmails
    subject = 'DNOW Weekend: Host Home Info - %s' % (hh.lastName)
    if debug:
        print('  To: ' + ', '.join(toList))
        print('  ' + subject + '\n\n')
        print(msgPlain)
        toList = ['dndmay2@gmail.com']
    # A debug flag besides True (like 1 or 'a') will set toList to dndmay2, but send email
    if debug is not True:
        send_mail(
            subject,
            msgPlain,
            'dndmay1@gmail.com',
            toList,
            html_message=msgHtml,
            auth_user='dndmay1@gmail.com',
            auth_password=os.environ.get('GMP'),
        )


def emailAllHostHomes(debug=False):
    hostHomesList = HostHome.objects.exclude(grade__contains='?').order_by('lastName')
    for hh in hostHomesList:
        if hh.student_set.count() > 0:
            print('Emailing %s : %s' % (hh.lastName, hh.email))
            emailHostHome(hh, debug=debug)
        else:
            print('SKIPPING %s because they do not have any students' % hh.lastName)


def emailDriver(driver, debug=False):
    driveSlots = driver.driveslot_set.all().order_by('time')
    hostHomes = {ds.hostHome for ds in driveSlots}
    dsHtml, dsText = generateDriveSlotHtml(driver, dest='email')
    hhHtml = ''
    hhText = ''
    for hh in hostHomes:
        hhHtml += generateHostHomeHtml(hh, driver=True)
        hhText += generateHostHomeText(hh, driver=True)

    churchStaffHtml, churchStaffText = generateChurchStaffHtml(dest='email')

    htmlContext = {
        'driver': driver,
        'driveSlots': dsHtml,
        'hostHomeHtml': hhHtml,
        'churchStaffHtml': churchStaffHtml
    }
    textContext = {
        'driver': driver,
        'driveSlots': dsText,
        'hostHomeHtml': hhText,
        'churchStaffHtml': churchStaffText
    }

    msgPlain = render_to_string('dnow/emailDrivers.txt', context=textContext)
    msgHtml = render_to_string('dnow/emailDrivers.html', context=htmlContext)

    toList = [driver.email]
    subject = 'DNOW Weekend: Driving Info - %s' % driver.lastName
    if debug:
        print('  To: ' + ', '.join(toList))
        print('  ' + subject + '\n\n')
        print(msgPlain)
        toList = ['dndmay2@gmail.com']
    # A debug flag besides True (like 1 or 'a') will set toList to dndmay2, but send email
    if debug is not True:
        send_mail(
            subject,
            msgPlain,
            'dndmay1@gmail.com',
            toList,
            html_message=msgHtml,
            auth_user='dndmay1@gmail.com',
            auth_password=os.environ.get('GMP'),
        )


def emailAllDrivers(debug=False):
    driverList = Driver.objects.order_by('lastName')
    for driver in driverList:
        if driver.driveslot_set.count() > 0:
            print('Emailing %s : %s' % (driver.lastName, driver.email))
            emailDriver(driver, debug=debug)
        else:
            print('SKIPPING %s because they do not have any assigned drive slots' % driver.lastName)


def emailCook(cook, debug=False):
    churchStaffHtml, churchStaffText = generateChurchStaffHtml(dest='email')
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
        'churchStaffHtml': churchStaffHtml
    }
    textContext = {
        'cook': cook,
        'hostHomeHtml': hhText,
        'churchStaffHtml': churchStaffText
    }

    msgPlain = render_to_string('dnow/emailCooks.txt', context=textContext)
    msgHtml = render_to_string('dnow/emailCooks.html', context=htmlContext)

    toList = [cook.email, 'ledeburs5@gmail.com']
    subject = 'DNOW Weekend: Cooking Info - %s' % cook.lastName
    if debug:
        print('  To: ' + ', '.join(toList))
        print('  ' + subject + '\n\n')
        print(msgPlain)
        toList = ['dndmay2@gmail.com']
    # A debug flag besides True (like 1 or 'a') will set toList to dndmay2, but send email
    if debug is not True:
        send_mail(
            subject,
            msgPlain,
            'dndmay1@gmail.com',
            toList,
            html_message=msgHtml,
            auth_user='dndmay1@gmail.com',
            auth_password=os.environ.get('GMP'),
        )


def emailAllCooks(debug=False):
    cookList = Cook.objects.order_by('lastName')
    for cook in cookList:
        if cook.meal_set.count() > 0:
            print('Emailing %s : %s' % (cook.lastName, cook.email))
            emailCook(cook, debug=debug)
        else:
            print('SKIPPING %s because they do not have any assigned meals' % cook.lastName)


def emailParent(student, debug=False):
    hh = student.hostHome
    # driver=True gives less details
    baseHtml = generateHostHomeHtml(hh, driver=True)
    baseText = generateHostHomeText(hh, driver=True)
    churchStaffHtml, churchStaffText = generateChurchStaffHtml(dest='email')
    textContext = {
        'hostHomeBaseHtml': baseText,
        'student': student,
        'hostHome': hh,
        'churchStaffHtml': churchStaffText
    }
    htmlContext = {
        'hostHomeBaseHtml': baseHtml,
        'student': student,
        'hostHome': hh,
        'churchStaffHtml': churchStaffHtml
    }
    msgPlain = render_to_string('dnow/emailParents.txt', context=textContext)
    msgHtml = render_to_string('dnow/emailParents.html', context=htmlContext)

    toList = [student.parentEmail]
    subject = 'DNOW Weekend: Details for student - %s %s' % (student.firstName, student.lastName)
    if debug:
        print('  To: ' + ', '.join(toList))
        print('  ' + subject + '\n\n')
        print(msgPlain)
        toList = ['dndmay2@gmail.com']
    # A debug flag besides True (like 1 or 'a') will set toList to dndmay2, but send email
    if debug is not True:
        connection = get_connection()
        connection.username = 'dndmay1@gmail.com'
        connection.password = os.environ.get('GMP')
        msg = EmailMultiAlternatives(subject, msgPlain, 'dndmay1@gmail.com', toList, connection=connection)
        msg.attach_alternative(msgHtml, "text/html")
        msg.attach_file('dnow/static/dnow/files/DNOWSchedule2018.docx')
        if not student.medicalForm:
            msg.attach_file('dnow/static/dnow/files/66763.pdf')
            msg.attach_file('dnow/static/dnow/files/66764.pdf')
        msg.send()
        # send_mail(
        #     subject,
        #     msgPlain,
        #     'dndmay1@gmail.com',
        #     toList,
        #     html_message=msgHtml,
        #     auth_user='dndmay1@gmail.com',
        #     auth_password=os.environ.get('GMP'),
        # )


def emailAllParents(debug=False):
    studentList = Student.objects.order_by('lastName')
    for student in studentList:
        print('Emailing %s %s: %s' % (student.firstName, student.lastName, student.parentEmail))
        emailParent(student, debug=debug)


def findBadEmailAddresses():
    parentEmails = [student.parentEmail.lower() for student in Student.objects.all()]
    hhEmails = [hh.email.lower() for hh in HostHome.objects.all()]
    cookEmails = [cook.email.lower() for cook in Cook.objects.all()]
    driverEmails = [driver.email.lower() for driver in Driver.objects.all()]
    badEmails = set()
    for e in hhEmails + cookEmails + driverEmails:
        if e not in parentEmails:
            badEmails.add(e)
    for e in badEmails:
        print('Possible wrong email: %s' % e)



