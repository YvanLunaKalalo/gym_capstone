from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from joblib import load
import pandas as pd
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from .models import Workout, UserProfile, UserWorkoutSession, UserProgress
from django.utils.timezone import now

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

# Define the view for workout recommendations
def workout_recommendation_view(request):
    template = loader.get_template("profile_form.html")  # Your form template
    
    if not request.user.is_authenticated:
        return redirect("login")

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

        # In this case, we'll just use the `Level`, `Fitness_Goal`, and `Fitness_Type` (categorical data) as a proxy
        profile_vector = vectorizer.transform([f"{Sex} {Age} {Height} {Weight} {Hypertension} {Diabetes} {BMI} {Level} {Fitness_Goal} {Fitness_Type}"])

        # Compute cosine similarity between profile and workout data
        similarity_scores = cosine_similarity(profile_vector, workout_features_matrix)

        # Get top 5 recommended workouts
        top_indices = similarity_scores[0].argsort()[-5:][::-1]
        recommended_workouts = workout_data.iloc[top_indices]

        # Save recommended workouts to the UserProgress model
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
            
        # Calculate dynamic progress
        # progress = calculate_progress(request.user)  # Dynamically calculate progress for the user

        # Pass recommended workouts to the template
        context = {
            "recommended_workouts" : recommended_workouts[['Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level']].to_dict(orient='records'),
            # "progress": progress,  # Pass progress to the template

        }
        
        # print(context["recommended_workouts"])

        return render(request, 'workout_recommendations.html', context)  # Render the output template

    return HttpResponse(template.render(context, request))

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

def complete_workout_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # Mark the current workout as completed
    progress_workout = UserProgress.objects.filter(user=request.user, completed=False).first()

    if progress_workout:
        progress_workout.completed = True
        progress_workout.progress_date = now()  # Set completion date
        progress_workout.save()

    # Check if there are more workouts to complete
    next_workout = UserProgress.objects.filter(user=request.user, completed=False).first()

    if not next_workout:
        # All workouts completed, recommend new ones
        user_profile = UserProfile.objects.get(user=request.user)
        recommend_new_workouts(request.user, user_profile)

        return redirect('workout_complete')

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
