from django.contrib import admin

from .models import Customer, Transaction, Category, RegistrationDevice, Product

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(RegistrationDevice)