from django.contrib import admin
from .models import User, Whitelist

admin.site.register(User)
admin.site.register(Whitelist)
