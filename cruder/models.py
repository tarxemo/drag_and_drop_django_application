from django.db import models
from authApp.models import *
  
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=200)
    def __str__(self):
        return self.title
        
class Order(models.Model):
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    borrower = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    librarian = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="processed_orders")
    book = models.ForeignKey(to="Book", on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True, null=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.librarian

class Person(models.Model):
    field_1730965012038 = models.CharField(max_length=100)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, null=True)


class BankAccount(models.Model):
    accoun_number = models.CharField(max_length=50)
    balance = models.CharField(max_length=150)

def __str__(self):
    return self.title
    