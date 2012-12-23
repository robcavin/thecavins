from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save

# Create your models here.
class Stream(models.Model) :
    group = models.ForeignKey(Group)

 
class Post(models.Model) :

    stream = models.ForeignKey(Stream)
    
    source_image = models.ImageField(upload_to='images',height_field='source_image_height',width_field='source_image_width', null=True)
    source_image_width = models.IntegerField(editable=False, null = True)
    source_image_height = models.IntegerField(editable=False, null = True)

    cropped_image = models.ImageField(upload_to='images',height_field='cropped_image_height',width_field='cropped_image_width', null=True)
    cropped_image_width = models.IntegerField(editable=False, null=True)
    cropped_image_height = models.IntegerField(editable=False, null=True)

    description = models.CharField(max_length=512,blank=True)
    
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model) :
    
    post = models.ForeignKey(Post)
    
    description = models.CharField(max_length=512,blank=True)
        
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserProfile(models.Model) :
    user = models.OneToOneField(User)
    
    source_image = models.ImageField(upload_to='images',height_field='source_image_height',width_field='source_image_width', null=True)
    source_image_width = models.IntegerField(editable=False, null=True)
    source_image_height = models.IntegerField(editable=False, null=True)

    cropped_image = models.ImageField(upload_to='images',height_field='cropped_image_height',width_field='cropped_image_width', null=True)
    cropped_image_width = models.IntegerField(editable=False, null=True)
    cropped_image_height = models.IntegerField(editable=False, null=True)
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

   