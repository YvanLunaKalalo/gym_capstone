from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from joblib import load
import pandas as pd
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from .models import Workout, UserProfile, UserWorkoutSession, UserProgress
from django.utils.timezone import now
from datetime import timedelta

# Load the pre-trained model
model1 = load('./Saved_Models/model1.joblib') # BMI
vectorizer = load('./Saved_Models/vectorizer.pkl') # Recommended Workout 2

# Load workout data (you might need to adjust the file path)
workout_data = pd.read_csv(settings.NOTEBOOKS_DIR / 'Datasets' / 'archive(2)' / 'megaGymDataset.csv')

# Combine relevant features from workout_data
workout_data['combined_features'] = workout_data['Title'] + " " + workout_data['Desc']
workout_data['combined_features'] = workout_data['combined_features'].fillna('')

# Transform workout features using the vectorizer
workout_features_matrix = vectorizer.transform(workout_data['combined_features'])

def bmi_view(request):
    template = loader.get_template('bmi.html')
    context = {}

    if request.method == 'POST':
        Gender = request.POST['Gender']
        Height = float(request.POST['Height'])
        Weight = float(request.POST['Weight'])

        # Ensure the feature names match those used during model training
        columns = [ 'Height', 'Weight', 'Gender_Female', 'Gender_Male']
        data = {
            'Height': [Height],
            'Weight': [Weight],
            'Gender_Female': [1 if Gender == 'female' else 0],
            'Gender_Male': [1 if Gender == 'male' else 0]
        }

        # Create a DataFrame with the correct feature order
        input_df = pd.DataFrame(data, columns=columns)

        # Predict using the loaded model
        y_pred = model1.predict(input_df)

        # Map predicted index to categories
        categories = ['Severely Underweight', 'Underweight', 'Normal', 'Overweight', 'Obesity', 'Severely Obesity']
        bmi_category = categories[y_pred[0]]

        context['result'] = bmi_category

    return HttpResponse(template.render(context, request))

def profile_form_view(request):
    template = loader.get_template("profile_form.html")  # Your form template
    
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == 'POST':
        # Get profile data from form submission
        Sex = request.POST.get('Sex', '')
        Age = request.POST.get('Age', '')
        Height = request.POST.get('Height', '')
        Weight = request.POST.get('Weight', '')
        Hypertension = request.POST.get('Hypertension', '')
        Diabetes = request.POST.get('Diabetes', '')
        Level = request.POST.get('Level', '')
        Fitness_Goal = request.POST.get('Fitness Goal', '')
        Fitness_Type = request.POST.get('Fitness Type', '')
        
        # Calculate BMI (BMI = weight in kg / (height in meters)^2)
        try:
            height_in_centimeters = float(Height) / 100
            weight_in_kg = float(Weight)
            BMI = weight_in_kg / (height_in_centimeters ** 2)
            BMI = round(BMI, 2)
        except (ValueError, ZeroDivisionError):
            BMI = None

        # Save profile data to session (or optionally store in the database)
        request.session['profile_data'] = {
            'Sex': Sex, 'Age': Age, 'Height': Height, 'Weight': Weight,
            'Hypertension': Hypertension, 'Diabetes': Diabetes, 'BMI': BMI,
            'Level': Level, 'Fitness_Goal': Fitness_Goal, 'Fitness_Type': Fitness_Type
        }

        # Redirect to workout recommendation view
        return redirect('workout_recommendation')

    return HttpResponse(template.render({}, request))

def workout_recommendation_view(request):
    # Check if profile data is in session
    profile_data = request.session.get('profile_data')

    if not request.user.is_authenticated or not profile_data:
        return redirect("profile_form")  # Redirect back to profile form if no data

    # Extract profile data from session
    Sex = profile_data.get('Sex', '')
    Age = profile_data.get('Age', '')
    Height = profile_data.get('Height', '')
    Weight = profile_data.get('Weight', '')
    BMI = profile_data.get('BMI', '')
    Hypertension = profile_data.get('Hypertension', '')
    Diabetes = profile_data.get('Diabetes', '')
    Level = profile_data.get('Level', '')
    Fitness_Goal = profile_data.get('Fitness_Goal', '')
    Fitness_Type = profile_data.get('Fitness_Type', '')

    # Process profile vector
    profile_vector = vectorizer.transform([f"{Sex} {Age} {Height} {Weight} {Hypertension} {Diabetes} {BMI} {Level} {Fitness_Goal} {Fitness_Type}"])

    # Compute cosine similarity between profile and workout data
    similarity_scores = cosine_similarity(profile_vector, workout_features_matrix)

    # Get top 5 recommended workouts
    top_indices = similarity_scores[0].argsort()[-5:][::-1]
    recommended_workouts = workout_data.iloc[top_indices]

    # Save recommended workouts to the database
    for _, workout in recommended_workouts.iterrows():
        workout_instance, created = Workout.objects.get_or_create(
            Title=workout['Title'],
            defaults={
                'Desc': workout['Desc'],
                'Type': workout['Type'],
                'BodyPart': workout['BodyPart'],
                'Equipment': workout.get('Equipment', 'None'),
                'Level': workout.get('Level', 'None')
            }
        )

        # Create a UserProgress entry for each recommended workout
        UserProgress.objects.get_or_create(
            user=request.user,
            workout=workout_instance,
            defaults={'progress': 0}  # Initialize progress to 0
        )
        
    # Prepare context with recommended workouts
    context = {
        "recommended_workouts": recommended_workouts[['Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level']].to_dict(orient='records'),
    }

    # Render workout recommendations template
    return render(request, 'workout_recommendations.html', context)

def workout_session_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # Fetch the user's current workout session from the UserProgress model
    progress_workout = UserProgress.objects.filter(user=request.user, completed=False).first()

    if not progress_workout:
        # If no uncompleted workouts, redirect to a completion or fallback page
        return redirect('workout_complete')

    current_workout = progress_workout.workout  # Get the workout associated with the progress

    context = {
        'workout': {
            'Title': current_workout.Title,
            'Desc': current_workout.Desc,
            'Type': current_workout.Type,
            'BodyPart': current_workout.BodyPart,
            'Equipment': current_workout.Equipment,
            'Level': current_workout.Level,
        },
        'progress_workout': progress_workout,  # Include current progress for display
    }

    return render(request, 'workout_session.html', context)

# def complete_workout_view(request):
#     if not request.user.is_authenticated:
#         return redirect("login")

#     # Mark the current workout as completed
#     progress_workout = UserProgress.objects.filter(user=request.user, completed=False).first()

#     if progress_workout:
#         progress_workout.completed = True
#         progress_workout.progress_date = now()  # Set completion date
#         progress_workout.save()

#     # Check if there are more workouts to complete
#     next_workout = UserProgress.objects.filter(user=request.user, completed=False).first()

#     if not next_workout:
#         # All workouts completed, recommend new ones
#         user_profile = UserProfile.objects.get(user=request.user)
#         recommend_new_workouts(request.user, user_profile)

#         return redirect('workout_complete')

#     return redirect('workout_session')

def complete_workout_view(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect("login")

    # Fetch all incomplete workouts for the user
    progress_workout = UserProgress.objects.filter(user=request.user, completed=False).first()

    # If there's an incomplete workout, mark it as completed
    if progress_workout:
        progress_workout.completed = True
        progress_workout.progress_date = now()  # Set the completion date to the current time
        progress_workout.save()

    # Check if all workouts for the current day are completed
    current_date = now().date()  # Get today's date
    day_workouts = UserProgress.objects.filter(user=request.user, progress_date=current_date)

    if day_workouts.count() == day_workouts.filter(completed=True).count():
        # If all workouts for the day are completed, move to the next day
        next_day = current_date + timedelta(days=1)
        next_workout = UserProgress.objects.filter(user=request.user, progress_date=next_day, completed=False).first()

        if not next_workout:
            # All workouts for this day are completed, move to day 2 or recommend new workouts if Day 6 is reached
            user_profile = UserProfile.objects.get(user=request.user)
            if current_date.day == 6:  # After Day 6, recommend new workouts
                recommend_new_workouts(request.user, user_profile)
                return redirect('workout_complete')  # Redirect to completion page once all workouts are completed
            else:
                # Proceed to the next day's workout session
                return redirect('workout_session')
        else:
            # Move to the next workout of the day
            return redirect('workout_session')

    # Redirect back to the current workout session if not all are completed
    return redirect('workout_session')

def recommend_new_workouts(user, profile):
    # Simulate generating workout recommendations based on the user's profile
    profile_vector = vectorizer.transform([f"{profile.Sex} {profile.Age} {profile.Height} {profile.Weight} {profile.Hypertension} {profile.Diabetes} {profile.BMI} {profile.Level} {profile.Fitness_Goal} {profile.Fitness_Type}"])

    # Compute cosine similarity and get top recommendations
    similarity_scores = cosine_similarity(profile_vector, workout_features_matrix)
    top_indices = similarity_scores[0].argsort()[-5:][::-1]
    recommended_workouts = workout_data.iloc[top_indices]

    # Save new workouts to UserProgress
    for _, workout in recommended_workouts.iterrows():
        workout_instance, created = Workout.objects.get_or_create(
            Title=workout['Title'],
            defaults={
                'Desc': workout['Desc'],
                'Type': workout['Type'],
                'BodyPart': workout['BodyPart'],
                'Equipment': workout.get('Equipment', 'None'),
                'Level': workout.get('Level', 'None')
            }
        )

        UserProgress.objects.get_or_create(
            user=user,
            workout=workout_instance,
            defaults={'progress': 0}  # Initialize progress to 0
        )

def workout_complete_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # Fetch all completed workouts
    completed_workouts = UserProgress.objects.filter(user=request.user, completed=True)

    # Calculate progress
    total_workouts = UserProgress.objects.filter(user=request.user).count()
    completed_count = completed_workouts.count()
    progress_percentage = (completed_count / total_workouts) * 100 if total_workouts > 0 else 0

    context = {
        'completed_workouts': completed_workouts,
        'progress_percentage': progress_percentage
    }

    return render(request, 'workout_complete.html', context)

def progress_tracker_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # Fetch all user progress records
    user_progress = UserProgress.objects.filter(user=request.user)

    # Calculate progress
    total_workouts = user_progress.count()
    completed_count = user_progress.filter(completed=True).count()
    progress_percentage = (completed_count / total_workouts) * 100 if total_workouts > 0 else 0

    context = {
        'user_progress': user_progress,
        'progress_percentage': progress_percentage,
        'total_workouts': total_workouts,
        'completed_count': completed_count
    }

    return render(request, 'progress_tracker.html', context)

def update_profile_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    # Fetch the user's profile
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('profile_not_found')  # Handle cases where the profile does not exist
    
    context = {}

    if request.method == 'POST':
        # Get the new height and weight from the form submission
        new_height = request.POST.get('Height', '')
        new_weight = request.POST.get('Weight', '')

        # Store the old height and weight before updating
        old_height = profile.Height
        old_weight = profile.Weight

        # Update the profile with new height and weight if provided
        if new_height:
            profile.Height = new_height
        if new_weight:
            profile.Weight = new_weight

        # Save the updated profile
        profile.save()

        # Compare old vs. new values
        height_changed = old_height != profile.Height
        weight_changed = old_weight != profile.Weight

        # Pass comparison results to the template
        context.update({
            'old_height': old_height,
            'old_weight': old_weight,
            'new_height': profile.Height,
            'new_weight': profile.Weight,
            'height_changed': height_changed,
            'weight_changed': weight_changed,
        })

    else:
        # If it's a GET request, just display the form with current values
        context.update({
            'old_height': profile.Height,
            'old_weight': profile.Weight,
            'new_height': profile.Height,
            'new_weight': profile.Weight,
        })

    return render(request, 'update_profile.html', context)