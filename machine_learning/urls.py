from django.urls import path
from . import views

urlpatterns = [
    path('bmi/', views.bmi_view, name="bmi"),
    path('recommend/', views.workout_recommendation_view, name="recommend"),
    path('workout-recommendations/', views.workout_recommendation_view, name='workout_recommendations'),
    path('start_workout_session/', views.start_workout_session_view, name='start_workout_session'),
    path('workout_session/', views.workout_session_view, name='workout_session'),
    path('next_workout/', views.next_workout_view, name='next_workout'),
    path('workout_complete/', views.workout_complete_view, name='workout_complete'),
    path('progress_tracker/', views.progress_tracker_view, name='progress_tracker'),
]