from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from personal.models import Contact
from machine_learning.models import Workout, UserProfile, UserProgress
from collections import defaultdict

def index_view(request):
    template = loader.get_template('index.html')

    # Check if the user has an ongoing workout session
    progress_workout = None
    if request.user.is_authenticated:
        progress_workout = UserProgress.objects.filter(user=request.user, completed=False).first()

    context = {
        'progress_workout': progress_workout,  # Pass this to the template
    } 
       
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
    
    if not request.user.is_authenticated:
        return redirect("login")

    # Get the user profile for the logged-in user
    user_profile = UserProfile.objects.filter(user=request.user).first()
    
    # Get all workouts
    workouts = Workout.objects.all()
    
    # Example grouping workouts by day
    workouts_by_day = defaultdict(list)  # Dictionary to store workouts by day
    day = 1
    for i, workout in enumerate(workouts):
        if (i % 5) == 0 and i > 0:
            day += 1
        workouts_by_day[day].append(workout)

    # Fetch only the workouts and progress associated with the logged-in user
    user_progress = UserProgress.objects.filter(user=request.user)
    
    # Calculate total completed workouts for each day
    user_progress_by_day = {}
    for day, day_workouts in workouts_by_day.items():
        completed_count = user_progress.filter(workout__in=day_workouts, completed=True).count()
        user_progress_by_day[day] = completed_count

    # Filter recommended workouts from UserProgress model
    workouts = [progress.workout for progress in user_progress]

    context = {
        'user_profile': user_profile,
        'workouts_by_day': workouts_by_day,
        'user_progress_by_day': user_progress_by_day,
        'user_progress': user_progress,
    }

    return render(request, 'dashboard.html', context)