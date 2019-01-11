from django.contrib import admin

# Register your models here.
from .models import Student, Parent, Contact, Driver, Cook, Leader, EmailTemplate, Profile


class ParentAdmin(admin.ModelAdmin):
    pass


class StudentAdmin(admin.ModelAdmin):
    pass


class DriverAdmin(admin.ModelAdmin):
    pass


class CookAdmin(admin.ModelAdmin):
    pass


class LeaderAdmin(admin.ModelAdmin):
    pass

class ProfileAdmin(admin.ModelAdmin):
    pass

class EmailTemplateAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Parent, ParentAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Cook, CookAdmin)
admin.site.register(Leader, LeaderAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
