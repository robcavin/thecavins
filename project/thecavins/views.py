# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.http import HttpResponse
from django.conf import settings
from thecavins.models import Stream, Post, Comment
from django.contrib.auth.models import User, Group

def homepage(request):
    return render(request, 'thecavins/homepage.html')
    
def stream(request,path) :
    group = Group.objects.get(name='Cavins')
    stream = Stream.objects.get(group=group)
    
    posts_to_display = []
    
    posts = list(stream.post_set.order_by('-updated_at'))
       
    for post in posts :
        comments = list(post.comment_set.order_by('created_at'))
        posts_to_display.append({'post':post,'comments':comments})
        
    return render(request, 'thecavins/demo.html', {'posts_to_display':posts_to_display})