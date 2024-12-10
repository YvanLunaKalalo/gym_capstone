from django.urls import path
from . import views

urlpatterns = [
    path('bmi/', views.bmi_view, name="bmi"),
    path('recommend/', views.workout_recommendation_view, name="recommend"),
    path('workout-recommendations/', views.workout_recommendation_view, name='workout_recommendations'),
    path('log_workout/', views.log_workout_session_view, name='log_workout_session'),
    path('progress_tracker/', views.view_progress_tracker_view, name='view_progress_tracker'),
]