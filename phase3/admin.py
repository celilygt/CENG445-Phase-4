from django.contrib import admin

from phase3.models import Container, Tracker, Cargo, MyUser

admin.site.register(MyUser)
admin.site.register(Cargo)
admin.site.register(Container)
admin.site.register(Tracker)

