from django.contrib import admin

from core.models import City, Contacts, Country, Person, State, User

admin.site.register(User)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Person)
admin.site.register(Contacts)
