from thecavins import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class ProfileInline(admin.StackedInline):
    model = models.UserProfile
    fk_name = 'user'

class UserAdminWProfile(UserAdmin):
    inlines = [ProfileInline,]

admin.site.register(models.Stream,admin.ModelAdmin)
admin.site.register(models.Post,admin.ModelAdmin)
admin.site.register(models.Comment,admin.ModelAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdminWProfile)
