from django.contrib import admin
from .models import Workout, UserProfile, WorkoutSession, ProgressTracker
from django.db.models import Count, Sum, F
from django.shortcuts import render

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level')
    search_fields = ('Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level')
    
    change_list_template = "admin/workout_change_list.html"  # Custom template for change list

    def changelist_view(self, request, extra_context=None):
        # Data for pie chart specific to workouts
        workout_data = Workout.objects.all().annotate(total_workouts=Count('id'))
        workout_titles = [workout.Title for workout in workout_data]
        workout_counts = [1] * len(workout_titles)  # Each workout counts as 1

        context = {
            'workout_titles': workout_titles,
            'workout_counts': workout_counts,
        }
        return super().changelist_view(request, extra_context=context)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'Sex', 'Age', 'Height', 'Weight', 'BMI', 'Fitness_Goal', 'Fitness_Type')
    search_fields = ('user__username', 'Sex', 'Fitness_Goal', 'Fitness_Type')
    
    change_list_template = "admin/userprofile_change_list.html"  # Custom template for change list

    def changelist_view(self, request, extra_context=None):
        # Data for pie chart specific to user profiles
        user_data = UserProfile.objects.all().annotate(total_profiles=Count('id'))
        fitness_goals = UserProfile.objects.values('Fitness_Goal').annotate(count=Count('Fitness_Goal'))
        fitness_goal_labels = [goal['Fitness_Goal'] for goal in fitness_goals]
        fitness_goal_counts = [goal['count'] for goal in fitness_goals]

        context = {
            'fitness_goal_labels': fitness_goal_labels,
            'fitness_goal_counts': fitness_goal_counts,
        }
        return super().changelist_view(request, extra_context=context)

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'workout', 'estimated_time_minutes', 'actual_time_minutes', 'session_date')
    search_fields = ('user_profile__user__username', 'workout__Title', 'session_date')
    list_filter = ('session_date',)
    
    change_list_template = "admin/workout_session_change_list.html"  # Custom template for WorkoutSession

    def changelist_view(self, request, extra_context=None):
        # Fetching workout sessions for chart data
        workout_sessions = WorkoutSession.objects.values('workout__Title').annotate(
            session_count=Count('id')
        )

        workout_titles = [session['workout__Title'] for session in workout_sessions]
        progress_counts = [session['session_count'] for session in workout_sessions]

        extra_context = extra_context or {}
        extra_context['workout_titles'] = workout_titles
        extra_context['progress_counts'] = progress_counts
        
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(ProgressTracker)
class ProgressTrackerAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'total_workouts', 'total_time_minutes')
    search_fields = ('user_profile__user__username',)

    change_list_template = "admin/progress_tracker_change_list.html"  # Custom template for ProgressTracker

    def changelist_view(self, request, extra_context=None):
        # Fetching progress data for chart
        progress_data = ProgressTracker.objects.values('user_profile__user__username').annotate(
            total_workouts=F('total_workouts'),
            total_time_minutes=F('total_time_minutes')
        )

        user_names = [progress['user_profile__user__username'] for progress in progress_data]
        total_workouts = [progress['total_workouts'] for progress in progress_data]

        extra_context = extra_context or {}
        extra_context['user_names'] = user_names
        extra_context['total_workouts'] = total_workouts
        
        return super().changelist_view(request, extra_context=extra_context)