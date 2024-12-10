from django.db import models
from django.conf import settings
from django.utils import timezone

class Workout(models.Model):
    Title = models.CharField(max_length=255)
    Desc = models.TextField()
    Type = models.CharField(max_length=50, default='None')
    BodyPart = models.CharField(max_length=50)
    Equipment = models.CharField(max_length=50, default='None')
    Level = models.CharField(max_length=50, default='None')

    def __str__(self):
        return self.Title
    
    class Meta:
        verbose_name = "List of Workouts"  # Singular name in admin
        verbose_name_plural = "Workouts"  # Plural name in admin

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Sex = models.CharField(max_length=10)
    Age = models.PositiveIntegerField()
    Height = models.FloatField()
    Weight = models.FloatField()
    Hypertension = models.CharField(max_length=10, default='No')
    Diabetes = models.CharField(max_length=10, default='No')
    BMI = models.FloatField()
    Level = models.CharField(max_length=50, default='Normal')
    Fitness_Goal = models.CharField(max_length=50, default='Weight_Loss')
    Fitness_Type = models.CharField(max_length=50, default='Cardio_Fitness')

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "List of User Profiles"  # Singular name in admin
        verbose_name_plural = "User Profiles"  # Plural name in admin
    
class WorkoutSession(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    workout = models.ForeignKey('Workout', on_delete=models.CASCADE)
    estimated_time_minutes = models.PositiveIntegerField()  # Estimated time in minutes
    actual_time_minutes = models.PositiveIntegerField(blank=True, null=True)  # Actual time spent on the workout
    session_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.workout.Title} ({self.session_date})"
    
    class Meta:
        verbose_name = "Workout Session"
        verbose_name_plural = "Workout Sessions"
        
class ProgressTracker(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.workout.Title} - {'Completed' if self.completed else 'Incomplete'}"