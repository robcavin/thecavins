from thecavins import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class ProfileInline(admin.StackedInline):
    model = models.UserProfile
    fk_name = 'user'
    
class UserAdminWProfile(UserAdmin):
    inlines = [ProfileInline,]

class ImagesInline(admin.TabularInline):
    model = models.Post.images.through

class PostAdmin(admin.ModelAdmin) :
    inlines = [ImagesInline,]
    exclude = ['images',]
    
admin.site.register(models.Stream,admin.ModelAdmin)
admin.site.register(models.Post,PostAdmin)
admin.site.register(models.Comment,admin.ModelAdmin)
admin.site.register(models.Image,admin.ModelAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdminWProfile)
