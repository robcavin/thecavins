# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.middleware.csrf import get_token
from django import forms
from django.http import HttpResponse
from django.conf import settings
from thecavins.models import Stream, Post, Comment, Image, UserProfile
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
#from django.contrib.auth import authenticate
#from django.contrib.auth import login as auth_login
from django.contrib.auth.views import login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.response import TemplateResponse
import json
from django.template.defaultfilters import register
from datetime import datetime
from django.utils.timezone import utc

@register.filter
def iso_to_date(value):
    (time,tz) = value.split('+')
    date = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
    date = date.replace(tzinfo=utc)
    return date

def render_api_or_html_response (request, template_name, data, context) :
    accepted_types = None

    if 'HTTP_ACCEPT' in request.META:
        accepted_types = [a.split(';')[0] for a in request.META['HTTP_ACCEPT'].split(',')]        

    # Prefer JSON response
    if accepted_types and 'application/json' in accepted_types :
        return HttpResponse(json.dumps(data))
    
    # Default to HTML response
    else :
        data.update(context)
        return render(request,template_name, data)
    

# Because login is a potential API endpoint, capture the results of the auth login and render appropriately
def login(request):
    response = auth_login(request)
    if isinstance(response,TemplateResponse) :
        return render_api_or_html_response(request,
                                           response.template_name,
                                           {'login_required':True,
                                            'csrfmiddlewaretoken':get_token(request)  # Has the side effect of setting the csrf cookie
                                            },
                                           response.context_data)
    
    else : return response

@login_required
def root(request) :
    groups = request.user.groups.all()
    if groups : group = groups[0]
    else : group = Group.objects.get(name='Cavins')
    return redirect('thecavins.views.stream', group.name)


@login_required
def about(request):
    return render(request, 'thecavins/about.html', {'active_page':'about'} )



class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email', 'password']
    
    username = forms.RegexField(
        label="Username", max_length=30, regex=r"^\w[\w-]+$",
        error_messages = {
            'invalid': "This value may contain only letters, numbers and "
                         "_ characters."})

    password = forms.CharField(widget=forms.widgets.HiddenInput, required=False)

class UserProfileForm(forms.ModelForm) :
    image_id = forms.CharField(widget=forms.widgets.HiddenInput, required=False)
    image = forms.ModelChoiceField(queryset=Image.objects.all(),widget=forms.widgets.HiddenInput, required=False)
    class Meta:
        model = UserProfile
        fields = ["nickname", "image", "image_id"]

@login_required
def account(request):
 
    if request.method == 'POST':
        form = MyUserChangeForm(request.POST,instance=request.user)
        pass_form = PasswordChangeForm(request.user,request.POST)
        prof_form = UserProfileForm(request.POST,instance=request.user.get_profile())
        
        if form.is_valid() and prof_form.is_valid() :
            form.save()             
            
            if prof_form.cleaned_data['image_id'] :
                prof_form.image = Image.objects.get(pk=prof_form.cleaned_data['image_id'])
           
            prof_form.save()

            messages.add_message(request, messages.SUCCESS, 'User information updated.')
            
        if pass_form.is_valid() :
            pass_form.save()
            messages.add_message(request, messages.SUCCESS, 'Password changed successfully.')
        
        else :
            if (not request.POST['old_password'] and
                not request.POST['new_password1'] and
                not request.POST['new_password2']) :
                pass_form = PasswordChangeForm(request.user)
    else :
        form = MyUserChangeForm(instance=request.user)
        pass_form = PasswordChangeForm(request.user)
        prof_form = UserProfileForm(instance=request.user.get_profile())
        
    return render(request, 'thecavins/account.html', {'form':form,'pass_form':pass_form,'prof_form':prof_form})



class PostForm(forms.Form):
    text = forms.CharField(label="",widget=forms.widgets.Textarea(attrs={'rows':4, 'class':'span10', 'placeholder':"Add a new post!" }), required=False)
    image_ids = forms.CharField(widget=forms.widgets.HiddenInput, required=False)

class CommentForm(forms.Form):
    text = forms.CharField(label="",widget=forms.widgets.Textarea(attrs={'rows':2, 'class':'span7', 'placeholder':"Add a comment!" }))
    
@login_required    
def stream(request,path) :
    
    group = Group.objects.get(name='Cavins')
    stream = Stream.objects.get(group=group)
    
    posts_to_display = []
    
    posts = list(stream.post_set.order_by('-updated_at')[:20])
       
    for post in posts :
        comments = list(post.comment_set.order_by('created_at'))
        posts_to_display.append({'post':post.as_dict(),'comments':[comment.as_dict() for comment in comments]})
    
    form = PostForm()
    comment_form = CommentForm()
    
    return render_api_or_html_response(request, 'thecavins/stream.html',
                                       {'stream_id': stream.id, 'posts_to_display':posts_to_display},
                                       {'form':form, 'comment_form':comment_form, 'active_page':'stream'})

@require_http_methods(["POST"])
def post_to_stream(request,stream_id) :

    stream = Stream.objects.get(pk=stream_id)

    if request.method == 'POST':
        
        # May upload an image directly from the phone
        submitted_image = None
        image_form = ImageUploadForm(request.POST, request.FILES)
        if image_form.is_valid() :
            print "YAY"
            new_image = Image()
            new_image.created_by = request.user
            new_image.original = image_form.cleaned_data['image']
            new_image.cropped = image_form.cleaned_data['image']
            new_image.save()
            submitted_image = new_image
       
        form = PostForm(request.POST, request.FILES)
        if form.is_valid() :
            
            images = []
            image_ids = [int(id) for id in form.cleaned_data['image_ids'].split(',') if id]
            if image_ids : images = Image.objects.filter(pk__in=image_ids)
            if submitted_image : images.append(submitted_image)

            #Make sure there is text OR an image.  Doesn't need to be both
            if form.cleaned_data['text'] or len(images) : 
                post = Post()
                post.description = form.cleaned_data['text'] or 'posted an image.'
                post.created_by = request.user
                post.stream = stream
                post.save()
    
                post.images = images
                
                # Send an email alerting of a post
                target_url = request.build_absolute_uri(reverse('thecavins.views.stream', args=(stream.id,)) + '#post-' + str(post.id))

                image_section = ""
                for image in post.images.all() :
                    image_section += '<br><img src="' + image.cropped.url +'">'
                                
                text_content = ("Please tell me if you see this.")
                html_content = (
                          "---- Reply above this line ----<br><br>"+
                          post.description + '<br><br>' +
                          image_section + '<br>' +
                          'Link to this post : ' + target_url
                          )

                subject = request.user.get_profile().nickname + ' posted to TheCavins.com'
                from_email='TheCavins@thecavins.com'
                recipient_list=[user.email for user in User.objects.filter(groups=stream.group).exclude(pk=request.user.pk) if user.email]
                
                msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=True)
            
    return redirect('thecavins.views.stream', stream.id)


@require_http_methods(["POST"])
def comment_to_post(request,post_id) :

    post = Post.objects.get(pk=post_id)
    target_url = request.build_absolute_uri(reverse('thecavins.views.stream', args=(post.stream.id,)) + '#post-' + str(post.id))
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid() :
            
            comment = Comment()
            comment.description = form.cleaned_data['text']
            comment.created_by = request.user
            comment.post = post
            comment.save()
            
            post.save()  # Update the 'updated_at' field
            
            # Send an email alerting of a post
            poster = comment.post.created_by.get_profile().nickname
            text_content = ("Please tell me if you see this.")

            html_content = (
                      "---- Reply above this line ----<br><br>"+
                      comment.description + '<br>' +
                      '<br> Original Post by ' + poster + ' : ' + comment.post.description + '<br><br>' +
                      'Link to this post : ' + target_url
                      )

            subject = (
                request.user.get_profile().nickname + ' commented on ' +
                poster + "'s Post on TheCavins.com"
                )
            from_email='TheCavins@thecavins.com'
            
            recipient_list=[user.email for user in User.objects.filter(groups=post.stream.group).exclude(pk=request.user.pk) if user.email]
            
            msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)
            
    return redirect(target_url)
            


# -------------------------------------------------------------------
# API Specific Endpoints
#
from django.views.decorators.csrf import csrf_protect

@csrf_protect
@login_required
def hello(request):
    user = request.user
    user.get_profile().save()  # Update last_active
    return HttpResponse(json.dumps({'username':user.username,
                                    'first_name':user.first_name,
                                    'last_name':user.last_name,
                                    }))

#   
# END API Specific Endpoints
#----------------------------------------------------------------------


#----------------------------------------------------------------------   
# IMAGE HANDLING
#
class ImageUploadForm(forms.Form):
    image = forms.ImageField()

@login_required
def image_upload(request):

    errors = [];
    
    if request.method == 'POST':
        image_form = ImageUploadForm(request.POST,request.FILES)
        if image_form.is_valid():
            file = image_form.cleaned_data['image']
            
            image = Image()
            image.original = file
            image.created_by = request.user
            image.save()
            return  HttpResponse('{"uploaded_image":{"url":"%s","id":%d,"width":%d,"height":%d}}' %
                                 (image.original.url, image.id, image.width, image.height))


import os
import StringIO
from PIL import Image as PILImage
from django.core.files.base import ContentFile

def crop_and_save(image, image_data, cropped_image_file_name, crop_rect, target_size):
    cropped_image_data = image_data.crop(crop_rect)
    cropped_image_data.thumbnail(target_size,PILImage.ANTIALIAS)    
    
    cropped_image_io = StringIO.StringIO()

    # Check if the image has an alpha layer and if so make it white.
    if cropped_image_data.mode in ["RGBA","LA"] :
        if cropped_image_data.mode == "RGBA" : index = 3
        else : index = 1
        cropped_image_data.load()    
        background = PILImage.new("RGB", cropped_image_data.size, (255, 255, 255))
        background.paste(cropped_image_data, mask=cropped_image_data.split()[index]) # 3 is the alpha channel
        background.save(cropped_image_io,'jpeg',quality=90)
    else: 
        if cropped_image_data.mode != "RGB": cropped_image_data = cropped_image_data.convert("RGB")  # Convert GIF/PNG w/pallette to JPEG friendly RGB
        cropped_image_data.save(cropped_image_io,'jpeg',quality=90) 

    cropped_image_file = ContentFile(cropped_image_io.getvalue())

    image.cropped.save(cropped_image_file_name,cropped_image_file)
    image.save()

@login_required
def image_crop(request, image_id):
    
    #XXX Need error checking
    crop_rect = eval(request.POST['crop_rect'])
    target_size = eval(request.POST['target_size'])
    image = Image.objects.get(pk=image_id)

    (image_path,file_name) = os.path.split(image.original.path)
    (file_name_prefix,file_name_ext) = file_name.rsplit('.',1)

    image_data = PILImage.open(image.original)
   
    cropped_image_file_name = file_name_prefix + '_cropped.jpg'

    crop_and_save(image, image_data, cropped_image_file_name, crop_rect, target_size)
    
    return  HttpResponse('{"cropped_image":{"url":"%s","id":%d}}' % (image.cropped.url, image.id))
#   
# END Image Handling
#--------------------------------------------------------------------