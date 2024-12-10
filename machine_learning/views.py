from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from joblib import load
import pandas as pd
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from .models import Workout, UserProfile, WorkoutSession, ProgressTracker
import time
from django.utils import timezone
from django.db.models import Count

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
        recommended_sessions = []
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
        
            # Create a WorkoutSession for each recommended workout
            session = WorkoutSession(
                user_profile=profile,
                workout=workout_obj,
                estimated_time_minutes=30  # Default estimated time, can be adjusted based on the workout
            )
            session.save()
            recommended_sessions.append(session)
        
            # Update the ProgressTracker model
        progress_tracker, created = ProgressTracker.objects.get_or_create(user_profile=profile)
        progress_tracker.update_progress()  # This updates the progress based on added sessions 
                
        # Pass recommended workouts to the template
        context = {
            "recommended_workouts" : recommended_workouts[['Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level']].to_dict(orient='records'),
        }
        context['progress'] = progress_tracker


        return render(request, 'workout_recommendations.html', context)  # Render the output template

    return HttpResponse(template.render(context, request))

def log_workout_session_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    workouts = Workout.objects.all()  # Fetch available workouts

    if request.method == 'POST':
        workout_id = request.POST.get('workout_id')
        estimated_time = request.POST.get('estimated_time')
        actual_time = request.POST.get('actual_time')
        
        workout = get_object_or_404(Workout, id=workout_id)
        session = WorkoutSession.objects.create(
            user_profile=user_profile,
            workout=workout,
            estimated_time_minutes=estimated_time,
            actual_time_minutes=actual_time,
            session_date=timezone.now()
        )
        
        # Update progress tracker
        progress_tracker, created = ProgressTracker.objects.get_or_create(user_profile=user_profile)
        progress_tracker.update_progress()

        return redirect('view_progress_tracker')  # Redirect to the progress tracker view

    return render(request, 'log_workout_session.html', {'workouts': workouts})

def view_progress_tracker_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    progress_tracker, created = ProgressTracker.objects.get_or_create(user_profile=user_profile)

    context = {
        'progress_tracker': progress_tracker
    }

    return render(request, 'progress_tracker.html', context)