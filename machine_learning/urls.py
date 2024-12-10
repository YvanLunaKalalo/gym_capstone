from django.urls import path
from . import views

urlpatterns = [
    path('bmi/', views.bmi_view, name="bmi"),
    path('recommend/', views.workout_recommendation_view, name="recommend"),
    path('workout-recommendations/', views.workout_recommendation_view, name='workout_recommendations'),
    path('workout-sessions/', views.workout_session_list_view, name='workout_session'),
    path('progress-tracker/', views.progress_tracker_view, name='progress_tracker'),
]