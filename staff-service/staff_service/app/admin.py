from django.contrib import admin
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'phone')
    search_fields = ('name', 'email')