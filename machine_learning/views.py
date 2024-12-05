from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from joblib import load
import pandas as pd
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from .models import Workout, UserProfile, UserProgress
import time

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

# Add a mapping for sets, reps, and days based on workout level
workout_level_mapping = {
    'Beginner': {'sets': 3, 'reps': 10, 'days_per_week': 3},
    'Intermediate': {'sets': 4, 'reps': 12, 'days_per_week': 4},
    'Advanced': {'sets': 5, 'reps': 15, 'days_per_week': 5},
}

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

def workout_recommendation_view(request):
    template = loader.get_template("profile_form.html")  # Your form template
    context = {}

    if request.method == 'POST':
        # Get profile data from form submission
        # 'ID': request.POST['ID'],
        # Use .get() to safely retrieve POST data
        Sex = request.POST.get('Sex', '')  # Default value is an empty string if 'Sex' is missing
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
            height_in_centimeters = float(Height) / 100  # Convert height from cm to meters
            weight_in_kg = float(Weight)  # Convert weight to kg
            BMI = weight_in_kg / (height_in_centimeters ** 2)
            BMI = round(BMI, 2)  # Round to two decimal places
        except (ValueError, ZeroDivisionError):
            # If there's an invalid input for height or weight, set BMI to None
            BMI = None

        # Save profile data in the database
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'Sex': Sex, 'Age': Age, 'Height': Height, 'Weight': Weight,
                'Hypertension': Hypertension, 'Diabetes': Diabetes, 'BMI': BMI,
                'Level': Level, 'Fitness_Goal': Fitness_Goal, 'Fitness_Type': Fitness_Type
            }
        )

        columns = ['Age', 'Height', 'Weight', 'BMI', 'Sex_Female', 'Sex_Male', 'Hypertension_No', 'Hypertension_Yes', 'Diabetes_No', 'Diabetes_Yes', 'Level_Normal', 'Level_Obuse', 'Level_Overweight', 'Level_Underweight', 'Fitness Goal_Weight Gain', 'Fitness Goal_Weight Loss', 'Fitness Type_Cardio Fitness', 'Fitness Type_Muscular Fitness']
        data = {
            'Age': [Age],
            'Height': [Height],
            'Weight' : [Weight],
            'BMI' : [BMI],
            'Sex_Female': [1 if Sex == 'Female' else 0],
            'Sex_Male': [1 if Sex == 'Male' else 0],
            'Hypertension_No' : [1 if Hypertension == 'No' else 0],
            'Hypertension_Yes' : [1 if Hypertension == 'Yes' else 0],
            'Diabetes_No' : [1 if Diabetes == 'No' else 0],
            'Diabetes_Yes' : [1 if Diabetes == 'Yes' else 0],
            'Level_Normal' : [1 if Level == 'Normal' else 0],
            'Level_Obuse' : [1 if Level == 'Obese' else 0],
            'Level_Overweight' : [1 if Level == 'Overweight' else 0],
            'Level_Underweight' : [1 if Level == 'Underweight' else 0],
            'Fitness Goal_Weight Gain' : [1 if Fitness_Goal == 'Weight Gain' else 0],
            'Fitness Goal_Weight Loss' : [1 if Fitness_Goal == 'Weight Loss' else 0],
            'Fitness Type_Cardio Fitness' : [1 if Fitness_Type == 'Cardio Fitness' else 0],
            'Fitness Type_Muscular Fitness' : [1 if Fitness_Type == 'Muscular Fitness' else 0],
        }
        
        # Inside the workout_recommendation_view function, adjust the workout_plan based on Fitness_Goal
    if Fitness_Goal == 'Weight Loss':
        workout_plan = workout_level_mapping.get(Level, {'sets': 3, 'reps': 10, 'days_per_week': 3})
        workout_plan['days_per_week'] = 5  # Typically higher frequency for weight loss (e.g., 5 days per week)
    elif Fitness_Goal == 'Muscular Fitness':
        workout_plan = workout_level_mapping.get(Level, {'sets': 4, 'reps': 12, 'days_per_week': 4})
        workout_plan['days_per_week'] = 4  # Lower frequency for muscular fitness (e.g., 4 days per week)
    else:
        workout_plan = workout_level_mapping.get(Level, {'sets': 3, 'reps': 10, 'days_per_week': 3})
        
        # Convert profile data to DataFrame
        # profile_df = pd.DataFrame(data, columns=columns)
        
        # Apply One-Hot Encoding
        # profile_df_encoded = pd.get_dummies(profile_df)

        # Debug: Check the encoded profile data
        # print("Encoded Profile Data: ", profile_df_encoded)

        # No need for combined_features for profile data, use direct inputs to calculate similarity
        # Here we simulate profile data as a single vector to compare with workout combined features

        # In this case, we'll just use the Level, Fitness_Goal, and Fitness_Type (categorical data) as a proxy
        profile_vector = vectorizer.transform([f"{Sex} {Age} {Height} {Weight} {Hypertension} {Diabetes} {BMI} {Level} {Fitness_Goal} {Fitness_Type}"])

        # Compute cosine similarity between profile and workout data
        similarity_scores = cosine_similarity(profile_vector, workout_features_matrix)

        # Get top 5 recommended workouts
        top_indices = similarity_scores[0].argsort()[-5:][::-1]
        recommended_workouts = workout_data.iloc[top_indices]

        # Save recommended workouts to the UserProgress model and Workout model
        for _, workout in recommended_workouts.iterrows():
            workout_obj, created = Workout.objects.get_or_create(
                Title=workout['Title'],
                defaults={
                    'Desc': workout['Desc'],
                    'Type': workout['Type'],
                    'BodyPart': workout['BodyPart'],
                    'Equipment': workout.get('Equipment', 'None'),
                    'Level': workout.get('Level', 'None')
                }
            )

            # Create UserProgress entry
            UserProgress.objects.get_or_create(
                user=request.user,
                workout=workout_obj,
                defaults={'progress': 0}  # Initialize progress at 0%
            )
            
        # Calculate dynamic progress
        progress = calculate_progress(request.user)  # Dynamically calculate progress for the user
        
        request.session['recommended_workouts'] = recommended_workouts.to_dict(orient='records')  # Store in session

        # Pass recommended workouts to the template
        context = {
            "recommended_workouts" : recommended_workouts[['Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level']].to_dict(orient='records'),
            "progress": progress,  # Pass progress to the template
            "workout_plan": workout_plan,  # Include workout plan details in the context
        }
        
        # print(context["recommended_workouts"])

        return render(request, 'workout_recommendations.html', context)  # Render the output template

    return HttpResponse(template.render(context, request))

import time
from django.shortcuts import render, redirect

def workout_session_view(request):
    workouts = request.session.get('recommended_workouts', [])  # Fetch workouts from session
    index = int(request.GET.get('index', 0))

    if index >= len(workouts):  # All workouts are completed
        return redirect('update_progress')  # Redirect to the dashboard

    current_workout = workouts[index]

    # Store the start time in the session if it's the first workout
    if 'start_time' not in request.session:
        request.session['start_time'] = time.time()

    # Check time elapsed for current workout
    elapsed_time = time.time() - request.session['start_time']

    # Calculate workout duration in minutes
    workout_duration = int(elapsed_time / 60)  # Convert seconds to minutes

    # Update elapsed time on each page load
    request.session['elapsed_time'] = workout_duration

    context = {
        'workout': current_workout,
        'index': index,
        'total_workouts': len(workouts),
        'workout_duration': workout_duration,  # Pass the workout time to the template
        'elapsed_time': request.session.get('elapsed_time', 0),
    }
    
    return render(request, 'workout_session.html', context)

def calculate_progress(user):
    """
    A helper function to dynamically calculate the user's progress
    based on workout completion, fitness goal, etc.
    """
    # Get the user profile
    user_profile = UserProfile.objects.get(user=user)

    # Example: Calculate progress based on the percentage of workouts completed per week
    total_workouts = Workout.objects.count()  # Total available workouts
    completed_workouts = UserProgress.objects.filter(user=user, progress=100).count()  # Workouts completed by user

    # Progress based on workouts completed
    workout_progress = (completed_workouts / total_workouts) * 100

    # Combine workout progress with a boost based on fitness goals
    progress = workout_progress

    # Example: Boost progress based on specific fitness goals
    if user_profile.Fitness_Goal == "Weight Loss":
        progress += 10  # Boost progress for specific goals (this is just an example)

    # Ensure progress doesn't exceed 100%
    return min(progress, 100)


def update_progress_view(request, workout_title):
    # Get the workout by its Title
    workout = get_object_or_404(Workout, Title=workout_title)
    
    # Get the user profile
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Fetch or initialize the user's progress for this workout
    progress_entry, created = UserProgress.objects.get_or_create(
        user=request.user, workout=workout,
        defaults={'progress': 0},  # Default progress when starting
    )

    if request.method == 'POST':
        # Increment the user's progress
        increment = int(request.POST.get('increment', 0))  # Get the increment value from the form
        progress_entry.progress = min(progress_entry.progress + increment, 100)  # Ensure it doesn't exceed 100%
        progress_entry.save()

    # Logic to calculate BMI based on user's weight and height
    height_in_meters = user_profile.height / 100  # Convert cm to meters
    bmi = user_profile.weight / (height_in_meters ** 2)  # Calculate BMI
    bmi_category = categorize_bmi(bmi)  # Categorize BMI

    progress_percentage = progress_entry.progress

    # Pass the data to the template
    context = {
        'workout': workout,
        'progress': progress_percentage,
        'user_profile': user_profile,
        'progress_date': progress_entry.progress_date,
        'bmi': bmi,
        'bmi_category': bmi_category
    }

    return render(request, 'progress_tracker.html', context)

def categorize_bmi(bmi):
    """Categorize the BMI value"""
    if bmi < 18.5:
        return 'Underweight'
    elif 18.5 <= bmi < 24.9:
        return 'Normal weight'
    elif 25 <= bmi < 29.9:
        return 'Overweight'
    else:
        return 'Obese'
