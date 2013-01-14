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
    
    def as_dict(self) :
        return {'original'      : {'url':self.original.url},
                'cropped'       : {'url':self.cropped.url},
                #'created_by'    : user_as_dict(self.created_by).update(self.created_by.get_profile().as_dict()),
                'created_at'    : self.created_at.isoformat(),
                'updated_at'    : self.updated_at.isoformat()
                }


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
        
    def as_dict(self) :
        return {'id'            : self.id,
                'stream_id'     : self.stream.id,
                'images'        : {'all':[image.as_dict() for image in self.images.all()]},
                'description'   : self.description,
                'created_by'    : user_as_dict(self.created_by),
                'created_at'    : self.created_at.isoformat(),
                'updated_at'    : self.updated_at.isoformat()
                }
    
class Comment(models.Model) :
    post = models.ForeignKey(Post)
    description = models.CharField(max_length=512,blank=True)    
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        str(self.post) +'-'+ self.created_by.username +'-'+ self.description

    def as_dict(self) :
        return {'id'            : self.id,
                'post_id'       : self.post.id,
                'description'   : self.description,
                'created_by'    : user_as_dict(self.created_by),
                'created_at'    : self.created_at.isoformat(),
                'updated_at'    : self.updated_at.isoformat()
                }

def user_as_dict(user) :
    return {'id'                : user.id,
            'username'          : user.username,
            'first_name'        : user.first_name,
            'last_name'         : user.last_name,
            'email'             : user.email,
            'get_profile'       : user.get_profile().as_dict()
            }

class UserProfile(models.Model) :
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=64)
    image = models.ForeignKey(Image)
    last_active = models.DateTimeField(auto_now=True)
    
    def as_dict(self) :
        return {'nickname'      : self.nickname,
                'image'         : self.image.as_dict(),
                'last_active'   : self.last_active.isoformat()
                }
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

   