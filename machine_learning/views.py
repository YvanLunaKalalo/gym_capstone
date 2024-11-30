from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from joblib import load
import pandas as pd
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from .models import Workout, UserProfile, UserProgress

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
                'Level': progress.workout.Level
            }
            for progress in existing_recommendations
        ]
        context = {
            "recommended_workouts": recommended_workouts,
            "progress": calculate_progress(request.user),
        }
        return render(request, 'workout_recommendations.html', context)

    if request.method == 'POST':
        # Extract form data and calculate BMI
        Sex = request.POST.get('Sex', '')
        Age = request.POST.get('Age', '')
        Height = request.POST.get('Height', '')
        Weight = request.POST.get('Weight', '')
        Fitness_Goal = request.POST.get('Fitness Goal', '')
        Fitness_Type = request.POST.get('Fitness Type', '')

        try:
            BMI = round(float(Weight) / ((float(Height) / 100) ** 2), 2)
        except (ValueError, ZeroDivisionError):
            BMI = None

        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'Sex': Sex, 'Age': Age, 'Height': Height, 'Weight': Weight, 'BMI': BMI,
                'Fitness_Goal': Fitness_Goal, 'Fitness_Type': Fitness_Type
            }
        )

        if not created:
            profile.Sex = Sex
            profile.Age = Age
            profile.Height = Height
            profile.Weight = Weight
            profile.BMI = BMI
            profile.Fitness_Goal = Fitness_Goal
            profile.Fitness_Type = Fitness_Type
            profile.save()

        profile_vector = vectorizer.transform([f"{Sex} {Age} {Height} {Weight} {BMI} {Fitness_Goal} {Fitness_Type}"])
        similarity_scores = cosine_similarity(profile_vector, workout_features_matrix)
        top_indices = similarity_scores[0].argsort()[-5:][::-1]
        recommended_workouts = workout_data.iloc[top_indices]

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
            UserProgress.objects.get_or_create(user=request.user, workout=workout_obj, defaults={'progress': 0})

        context = {
            "recommended_workouts": recommended_workouts[['Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level']].to_dict(orient='records'),
            "progress": calculate_progress(request.user),
        }

        return render(request, 'workout_recommendations.html', context)

    return render(request, 'profile_form.html')

def calculate_progress(user):
    total_workouts = UserProgress.objects.filter(user=user).count()
    completed_workouts = UserProgress.objects.filter(user=user, progress=100).count()

    if total_workouts == 0:
        return 0

    return min((completed_workouts / total_workouts) * 100, 100)

def update_progress_view(request, workout_title):
    workout = get_object_or_404(Workout, Title=workout_title)
    progress_entry, created = UserProgress.objects.get_or_create(
        user=request.user, workout=workout, defaults={'progress': 0})

    if request.method == 'POST':
        increment = int(request.POST.get('increment', 0))
        progress_entry.progress = min(progress_entry.progress + increment, 100)
        progress_entry.save()

    context = {
        'workout': workout,
        'progress': progress_entry.progress,
    }
    return render(request, 'progress_tracker.html', context)