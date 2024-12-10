from django.urls import path
from . import views

urlpatterns = [
    path('bmi/', views.bmi_view, name="bmi"),
    path('recommend/', views.workout_recommendation_view, name="recommend"),
    path('workout-recommendations/', views.workout_recommendation_view, name='workout_recommendations'),
    path('workout-session/', views.workout_session_view, name='workout_session'),
    path('track-progress/', views.progress_tracker_view, name='track_progress'),
]