from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from joblib import load
import pandas as pd
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from .models import Workout, UserProfile, UserProgress
from django.contrib.auth.decorators import login_required

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

@login_required
def workout_recommendation_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None

    existing_recommendations = UserProgress.objects.filter(user=request.user).select_related('workout')

    if profile and existing_recommendations.exists():
        recommended_workouts = [
            {
                'Title': progress.workout.Title,
                'Desc': progress.workout.Desc,
                'Type': progress.workout.Type,
                'BodyPart': progress.workout.BodyPart,
                'Equipment': progress.workout.Equipment,
                'Level': progress.workout.Level,
                'is_completed': progress.is_completed,
                'id': progress.workout.id  # Add workout ID for marking completion
            }
            for progress in existing_recommendations
        ]

        context = {
            "recommended_workouts": recommended_workouts,
            "progress": calculate_progress(request.user),
        }

        return render(request, 'workout_recommendations.html', context)
    
    if request.method == 'POST':
        # Collect form data
        Sex = request.POST.get('Sex', '')
        Age = request.POST.get('Age', '')
        Height = request.POST.get('Height', '')
        Weight = request.POST.get('Weight', '')
        Hypertension = request.POST.get('Hypertension', '')
        Diabetes = request.POST.get('Diabetes', '')
        Level = request.POST.get('Level', '')
        Fitness_Goal = request.POST.get('Fitness Goal', '')
        Fitness_Type = request.POST.get('Fitness Type', '')

        # Calculate BMI
        try:
            height_in_meters = float(Height) / 100
            weight_in_kg = float(Weight)
            BMI = weight_in_kg / (height_in_meters ** 2)
            BMI = round(BMI, 2)
        except (ValueError, ZeroDivisionError):
            BMI = None

        # Generate workout recommendations
        profile_vector = vectorizer.transform([f"{Sex} {Age} {Height} {Weight} {Hypertension} {Diabetes} {BMI} {Level} {Fitness_Goal} {Fitness_Type}"])
        similarity_scores = cosine_similarity(profile_vector, workout_features_matrix)
        top_indices = similarity_scores[0].argsort()[-5:][::-1]
        recommended_workouts = workout_data.iloc[top_indices]

        # Save recommendations for the user in UserProgress
        for _, workout in recommended_workouts.iterrows():
            workout_obj, created = Workout.objects.get_or_create(
                Title=workout['Title'],
                defaults={
                    'Desc': workout['Desc'],
                    'Type': workout['Type'],
                    'BodyPart': workout['BodyPart'],
                    'Equipment': workout.get('Equipment', 'None'),
                    'Level': workout.get('Level', 'Beginner')
                }
            )
            UserProgress.objects.get_or_create(
                user=request.user,
                workout=workout_obj,
                defaults={'progress': 0, 'is_completed': False}
            )

        context = {
            "recommended_workouts": recommended_workouts[['Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level']].to_dict(orient='records'),
            "progress": calculate_progress(request.user),
        }

        return render(request, 'workout_recommendations.html', context)

    return render(request, 'profile_form.html')


@login_required
def mark_workout_done(request, workout_id):
    progress = get_object_or_404(UserProgress, user=request.user, workout_id=workout_id)
    progress.is_completed = True
    progress.progress = 100  # Mark progress as completed
    progress.save()
    return redirect('workout_recommendation_view')


def calculate_progress(user):
    user_progress = UserProgress.objects.filter(user=user)
    if not user_progress.exists():
        return 0
    total_workouts = user_progress.count()
    completed_workouts = user_progress.filter(is_completed=True).count()
    return int((completed_workouts / total_workouts) * 100)
