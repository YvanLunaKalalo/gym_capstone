from django.urls import path
from . import views

urlpatterns = [
    path('bmi/', views.bmi_view, name="bmi"),
    path('recommend/', views.workout_recommendation_view, name="recommend"),
    path('workout-recommendations/', views.workout_recommendation_view, name='workout_recommendations'),
    path('progress/<str:workout_title>/', views.update_progress_view, name='update_progress'),
]