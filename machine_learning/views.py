from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from joblib import load
import pandas as pd
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from .models import Workout, UserProfile, UserWorkoutSession, UserProgress

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
            UserProgress.objects.get_or_create(
                user=request.user,
                workout=Workout.objects.get_or_create(
                    Title=workout['Title'],
                    defaults={
                        'Desc': workout['Desc'],
                        'Type': workout['Type'],
                        'BodyPart': workout['BodyPart'],
                        'Equipment': workout.get('Equipment', 'None'),
                        'Level': workout.get('Level', 'None')
                    }
                )[0],
                defaults={'progress': 0}  # Initialize progress
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

def start_workout_session_view(request):
    recommended_workouts = get_recommended_workouts_for_user(request.user)
    
    if not recommended_workouts.exists():
        return redirect('no_workouts')  # Handle the case where there are no recommended workouts

    # Start a session with the first recommended workout
    first_workout = recommended_workouts.first()
    session, created = UserWorkoutSession.objects.get_or_create(
        user=request.user,
        defaults={'current_workout': first_workout}
    )

    return redirect('workout_session')

# A function to get recommended workouts based on user's profile or preferences
def get_recommended_workouts_for_user(user):
    # Example logic for getting recommended workouts based on user's profile
    # You may want to use a recommendation algorithm here
    return Workout.objects.filter(recommended_for=user.profile.fitness_goal)

def workout_session_view(request):
    session = get_object_or_404(UserWorkoutSession, user=request.user)
    current_workout = session.current_workout
    if not current_workout:
        return redirect('no_workouts')  # Handle if there is no current workout

    context = {
        'workout': {
            'title': current_workout.Title,  # Use correct field names from your Workout model
            'desc': current_workout.Desc,
            'type': current_workout.Type,
            'body_part': current_workout.BodyPart,
            'equipment': current_workout.Equipment,
            'level': current_workout.Level
        }
    }

    return render(request, 'workout_session.html', context)

def next_workout_view(request):
    session = get_object_or_404(UserWorkoutSession, user=request.user)
    current_workout = session.current_workout

    if current_workout:
        # Mark the current workout as completed
        UserProgress.objects.update_or_create(
            user=request.user,
            workout=current_workout,
            defaults={'completed': True}
        )

        # Find the next workout in the sequence
        next_workout = Workout.objects.filter(id__gt=current_workout.id).first()
        if next_workout:
            session.current_workout = next_workout
            session.save()
            return redirect('workout_session')

        # If no more workouts, mark the session as completed
        session.completed = True
        session.save()
        return redirect('workout_complete')

    return redirect('no_workouts')

def workout_complete_view(request):
    session = get_object_or_404(UserWorkoutSession, user=request.user)
    progress = UserProgress.objects.filter(user=request.user, completed=True).count()
    total_workouts = Workout.objects.all().count()

    progress_percentage = int((progress / total_workouts) * 100) if total_workouts > 0 else 0

    context = {
        'progress_percentage': progress_percentage,
        'completed_message': 'Congratulations! You have completed all the workouts!'
    }

    return render(request, 'workout_complete.html', context)

def progress_tracker_view(request):
    progress_list = UserProgress.objects.filter(user=request.user, completed=True)
    progress_percentage = progress_list.count() * 100 / Workout.objects.count()

    context = {
        'progress_percentage': progress_percentage,
        'completed_workouts': progress_list
    }

    return render(request, 'progress_tracker.html', context)