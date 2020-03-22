from django.contrib import admin

from .models import Customer, Transaction, Category, RegistrationDevice

admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(RegistrationDevice)
