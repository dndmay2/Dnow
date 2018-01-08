from __future__ import unicode_literals

from django.db import models
from localflavor.us import models as usmodels

GRADE_CHOICES = (
    ('?', '?'),
    ('7', '7th'),
    ('8', '8th'),
    ('9', '9th'),
    ('10', '10th'),
    ('11', '11th'),
    ('12', '12th')
)

SHIRT_SIZES = (
    ('Small',   'S'),
    ('Med',     'M'),
    ('Large',   'L'),
    ('XL',      'XL'),
    # ('X Large',      'XL'),
    ('XXL',     'XXL'),
    ('XXXL',    'XXXL'),
)

DRIVE_SLOTS = (
    ('driveSlot1', '1 Fri, 8:45-9:30 pm'),
    ('driveSlot2', '2 Sat, 9:50-10:30 am'),
    ('driveSlot3', '3 Sat, 12:30-4:00 pm'),
    ('driveSlot4', '4 Sat, 6:20-6:45 pm'),
    ('driveSlot5', '5 Sat, 8:50-9:30 pm'),
    ('driveSlot6', '6 Sun, 8:20-8:45 am'),
)


# Create your models here.
class Contact(models.Model):
    firstName = models.CharField(max_length=30, default='')
    lastName = models.CharField(max_length=30, default='')
    phone = usmodels.PhoneNumberField(default='')
    email = models.EmailField(default='')
    street = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=90, default='Fairview')
    state = usmodels.USStateField(default='TX')
    zipCode = usmodels.USZipCodeField(default='75069')

    '''
    This model will then not be used to create any database table.
    Instead, when it is used as a base class for other models, its
    fields will be added to those of the child class.
    '''
    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s, %s' % (self.lastName, self.firstName)


class Parent(Contact):
    host = models.BooleanField(default=False)


class Driver(Contact):
    carCapacity = models.IntegerField()
    bgCheck = models.BooleanField(default=False)
    tshirtSize = models.CharField(max_length=4, choices=SHIRT_SIZES, default='M')

    def __str__(self):
        return '%s %s' % (self.firstName, self.lastName)


class HostHome(Contact):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True)
    grade = models.CharField(max_length=15, choices=GRADE_CHOICES, default='?')
    gender = models.CharField(max_length=2, choices=(('M', 'Male'), ('F', 'Female')), default='M')
    bgCheck = models.BooleanField(default=False)
    tshirtSize = models.CharField(max_length=16, choices=SHIRT_SIZES, default='M')
    allergy = models.CharField(max_length=80, default='')

    def __str__(self):
        return '%s, %s %s' % (self.lastName, self.grade, self.gender)



class Leader(Contact):
    hostHome = models.ForeignKey(HostHome, on_delete=models.CASCADE, null=True, blank=True)
    bgCheck = models.BooleanField(default=False)
    tshirtSize = models.CharField(max_length=16, choices=SHIRT_SIZES, default='M')
    isDriving = models.BooleanField(default=False)
    churchStaff = models.BooleanField(default=False)
    allergy = models.CharField(max_length=80, default='')

    def __str__(self):
        return '%s %s' % (self.firstName, self.lastName)


class Student(Contact):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True)
    hostHome = models.ForeignKey(HostHome, on_delete=models.CASCADE, null=True, blank=True)
    friendName = models.CharField(max_length=80, default='')
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default='?')
    gender = models.CharField(max_length=2, choices=(('M', 'Male'), ('F', 'Female')), default='M')
    dateRegistered = models.DateField(null=True, blank=True)
    amountPaid = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    churchMember = models.BooleanField(default=False)
    medicalForm = models.BooleanField(default=False)
    tshirtSize = models.CharField(max_length=16, choices=SHIRT_SIZES, default='M')
    parentPhone = usmodels.PhoneNumberField(default='')
    parentEmail = models.EmailField(default='')
    allergy = models.CharField(max_length=80, default='')

    def __str__(self):
        return '%s %s, %s %s' % (self.firstName, self.lastName, self.grade, self.gender)


class Cook(Contact):
    tshirtSize = models.CharField(max_length=4, choices=SHIRT_SIZES, default='-')

    def __str__(self):
        return '%s %s' % (self.firstName, self.lastName)


class Meal(models.Model):
    hostHome = models.ForeignKey(HostHome, on_delete=models.CASCADE, null=True, blank=True)
    cook = models.ForeignKey(Cook, on_delete=models.CASCADE, null=True, blank=True)
    time = models.CharField(max_length=40, default='')

    def __str__(self):
        return "%s %s - %s @ %s" % (self.cook.firstName, self.cook.lastName, self.time, self.hostHome.lastName)


class DriveSlot(models.Model):
    hostHome = models.ForeignKey(HostHome, on_delete=models.CASCADE, null=True, blank=True)
    drivers = models.ManyToManyField(Driver)
    # time = models.DateTimeField(null=True, blank=True)
    time = models.CharField(max_length=20, default='')

    def __str__(self):
        return "%s @ %s - %d drivers" % (self.time, self.hostHome.lastName, self.drivers.count())

