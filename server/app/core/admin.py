from django.contrib import admin

from . import models


admin.site.register(models.Stream)
admin.site.register(models.Donation)
admin.site.register(models.CustomUser)
