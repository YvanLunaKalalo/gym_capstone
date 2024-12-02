from django.urls import path
from . import views

urlpatterns = [
    path('bmi/', views.bmi_view, name="bmi"),
    path('recommend/', views.workout_recommendation_view, name="recommend"),
    path('workout-recommendations/', views.workout_recommendation_view, name='workout_recommendations'),
    # path('progress/<str:workout_title>/', views.update_progress_view, name='update_progress'),
    path('workout_session/<str:workout_title>/', views.workout_session_view, name='workout_session'),
    path('workout_dashboard/', views.workout_dashboard_view, name='workout_dashboard'),
]