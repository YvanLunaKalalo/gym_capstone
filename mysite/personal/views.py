from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from personal.models import Contact
from machine_learning.models import Workout, UserProfile, UserProgress

def index_view(request):
    template = loader.get_template('index.html')

    context = {}

    if request.method=="POST":
        contact = Contact()
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        contact.name = name
        contact.email = email
        contact.subject = subject
        contact.message = message
        contact.save()
        return render(request, "contact_done.html")

    return HttpResponse(template.render(context, request))

def dashboard_view(request):
    workouts = Workout.objects.all()  # Get all workouts
    user_profile = None
    user_progress = None
    
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)  # Get user's profile
        except UserProfile.DoesNotExist:
            user_profile = None  # If profile doesn't exist, keep it None
        
        user_progress = UserProgress.objects.filter(user=request.user)  # Get user's progress
    
    context = {
        'workouts': workouts,
        'user_profile': user_profile,
        'user_progress': user_progress,
    }
    
    return render(request, 'dashboard.html', context)