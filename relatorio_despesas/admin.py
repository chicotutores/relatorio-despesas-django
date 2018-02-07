# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

class ExpenseAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'date', 'type')
    list_display = ('date', 'type', 'user')
    ordering = ('date',)

class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ('project', 'client', 'document', 'user__first_name', 'user__first_name',)
    list_display = ('user', 'document', 'project', 'client')
    exclude = ('balance',)
    ordering = ('user__first_name',)

admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Employee, EmployeeAdmin)