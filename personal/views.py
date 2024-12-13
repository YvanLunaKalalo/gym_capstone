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
    # Get the user profile for the logged-in user
    user_profile = UserProfile.objects.filter(user=request.user).first()

    # Fetch only the workouts and progress associated with the logged-in user
    user_progress = UserProgress.objects.filter(user=request.user)

    # Filter recommended workouts from UserProgress model
    workouts = [progress.workout for progress in user_progress]

    context = {
        'user_profile': user_profile,
        'workouts': workouts,
        'user_progress': user_progress,
    }

    return render(request, 'dashboard.html', context)