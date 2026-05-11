from django.db import models


class User(models.Model):
    user = models.TextField(default=None)

    class Meta:
        db_table = 'stock_user'
        managed = False

    def __str__(self):
        return self.user


class Country(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'stock_country'
        managed = False

    def __str__(self):
        return self.name


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'stock_state'
        managed = False

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'stock_city'
        managed = False

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'stock_person'
        managed = False

    def __str__(self):
        return self.name


class Contacts(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=100, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='stock/images', null=True, blank=True)

    class Meta:
        db_table = 'stock_contacts'
        managed = False

    def __str__(self):
        return str(self.name)
