from django.db import models
from django.conf import settings

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
    Hypertension = models.CharField(max_length=3, default='No')
    Diabetes = models.CharField(max_length=3, default='No')
    BMI = models.FloatField()
    Level = models.CharField(max_length=50, default='Normal')
    Fitness_Goal = models.CharField(max_length=5, default='Weight_Loss')
    Fitness_Type = models.CharField(max_length=50, default='Cardio_Fitness')

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "List of User Profiles"  # Singular name in admin
        verbose_name_plural = "User Profiles"  # Plural name in admin
    
class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField()  # Percentage or count of completed workouts
    date = models.DateField(auto_now_add=True)
    progress_date = models.DateField(auto_now=True)  # Automatically update the date whenever the progress is updated
    
    def __str__(self):
        return f"{self.user.username} - {self.workout.Title} - {self.progress}%"
    
    class Meta:
        verbose_name = "List of User Progress"  # Singular name in admin
        verbose_name_plural = "User Progress"  # Plural name in admin