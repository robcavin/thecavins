from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.conf import settings
class Image(models.Model) :

    original = models.ImageField(upload_to='images',height_field='height',width_field='width')
    width = models.IntegerField(editable=False)
    height = models.IntegerField(editable=False)

    cropped = models.ImageField(upload_to='images',null=True, blank=True, height_field='cropped_height',width_field='cropped_width')
    cropped_width = models.IntegerField(editable=False, null=True)
    cropped_height = models.IntegerField(editable=False, null=True)

    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.original.name # just setting this to role for now since description has been removed

# Create your models here.
class Stream(models.Model) :
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=64)
    
    def __unicode__(self):
        return self.name
 
class Post(models.Model) :
    stream = models.ForeignKey(Stream)
    images = models.ManyToManyField(Image, related_name='posts')
    description = models.CharField(max_length=512,blank=True)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.stream.name +' - '+ self.created_by.username +' - '+ self.description[0:32]
        
class Comment(models.Model) :
    post = models.ForeignKey(Post)
    description = models.CharField(max_length=512,blank=True)    
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        str(self.post) +'-'+ self.created_by.username +'-'+ self.description

class UserProfile(models.Model) :
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=64)
    image = models.ForeignKey(Image)
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

   