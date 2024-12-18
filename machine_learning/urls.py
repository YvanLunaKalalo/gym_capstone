from django.urls import path
from . import views

urlpatterns = [
    path('bmi/', views.bmi_view, name="bmi"),
    path('recommend/', views.workout_recommendation_view, name="recommend"),
    path('session/', views.workout_session_view, name="workout_session"),
    path('next/', views.next_workout_view, name="next_workout"),
    path('complete/', views.workout_complete_view, name="workout_complete"),
    path('progress-tracker/', views.progress_tracker_view, name="progress_tracker"),
]