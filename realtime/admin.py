from django.contrib import admin
from realtime.models import Employee, EmployeeRegister
# Register your models here.

admin.site.register(Employee)

class EmployeeRegisterAdmin(admin.ModelAdmin):
    list_display  = ('employee_object','date','time','alert')

admin.site.register(EmployeeRegister,EmployeeRegisterAdmin)