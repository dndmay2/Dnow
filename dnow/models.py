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
    ('XXL',     'XXL'),
    ('XXXL',    'XXXL'),
)

DRIVE_SLOTS = (
    ('driveSlot1', 'Fri, 8:50-9:30 pm'),
    ('driveSlot2', 'Sat, 9:50-10:30 am'),
    ('driveSlot3', 'Sat, 11:50 am-12:20 pm'),
    ('driveSlot4', 'Sat, 1:00-4:00 pm'),
    ('driveSlot5', 'Sat, 6:20-6:45 pm'),
    ('driveSlot6', 'Sat, 8:45-9:30 pm'),
    ('driveSlot7', 'Sun, 8:15-8:45 am'),
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


class HostHome(Contact):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True)
    grade = models.CharField(max_length=15, choices=GRADE_CHOICES, default='?')
    gender = models.CharField(max_length=2, choices=(('M', 'Male'), ('F', 'Female')), default='M')
    bgCheck = models.BooleanField(default=False)


class Student(Contact):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True)
    hostHome = models.ForeignKey(HostHome, on_delete=models.CASCADE, null=True, blank=True)
    friendName = models.CharField(max_length=40, default='')
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default='?')
    gender = models.CharField(max_length=2, choices=(('M', 'Male'), ('F', 'Female')), default='M')
    dateRegistered = models.DateField(null=True, blank=True)
    amountPaid = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    churchMember = models.BooleanField(default=False)
    medicalForm = models.BooleanField(default=False)
    tshirtSize = models.CharField(max_length=4, choices=SHIRT_SIZES, default='M')
    parentPhone = usmodels.PhoneNumberField(default='')


class Driver(Contact):
    hostHome = models.ForeignKey(HostHome, on_delete=models.CASCADE, null=True, blank=True)
    carCapacity = models.IntegerField()
    bgCheck = models.BooleanField(default=False)
    driveSlot1 = models.BooleanField(default=False)
    driveSlot2 = models.BooleanField(default=False)
    driveSlot3 = models.BooleanField(default=False)
    driveSlot4 = models.BooleanField(default=False)
    driveSlot5 = models.BooleanField(default=False)
    driveSlot6 = models.BooleanField(default=False)
    driveSlot7 = models.BooleanField(default=False)


class Cook(Contact):
    hostHome = models.ForeignKey(HostHome, on_delete=models.CASCADE, null=True, blank=True)
    meal1 = models.BooleanField(default=False)
    meal2 = models.BooleanField(default=False)

