import pytz
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, default="No name")

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, default="Product name")
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)
    shown = models.BooleanField(default=True, null=False)

    def __str__(self):
        return self.name


class Customer(models.Model):
    first_name = models.CharField(max_length=60, null=False, default="Voornaam")
    last_name = models.CharField(max_length=60, null=False, default="Achternaam")
    email = models.EmailField(null=False)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Transaction(models.Model):
    buyer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    date_time = models.DateTimeField(auto_now_add=True)
    item_bought = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)

    def get_date_time_in_timezone(self, time_zone: str = 'Europe/Amsterdam'):
        return self.date_time.astimezone(pytz.timezone(time_zone))

    def __str__(self):
        return str(self.buyer) + " bought " + str(self.item_bought) + " for " + str(self.price)


class RegistrationDevice(models.Model):
    uuid = models.CharField(max_length=16, null=False, blank=False)
    date_time = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return "Device of " + str(self.owner) + " with uuid " + str(self.uuid)
