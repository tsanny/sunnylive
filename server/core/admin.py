from django.contrib import admin

from .models import Stream, Donation, CustomUser, Comment


admin.site.register((Stream, Donation, CustomUser, Comment))
