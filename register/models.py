from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from projects.models import Project

# Create your models here.
class Company(models.Model):
    social_name = models.CharField(max_length=80)
    name = models.CharField(max_length=80)
    email = models.EmailField()
    city = models.CharField(max_length=50)
    found_date = models.DateField()

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ('name',)


    def __str__(self):
        return (self.name)

class UserProfile(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    project = models.ManyToManyField(Project, blank=True)
    friends = models.ManyToManyField('self', blank=True)
    img    = models.ImageField(upload_to='core/avatar', blank=True, default='core/avatar/blank_profile.png')

    def __str__(self):
        return (str(self.user))

    def invite(self, invite_profile):
        invite = Invite(inviter=self, invited=invite_profile)
        invites = invite_profile.received_invites.filter(inviter_id=self.id)
        if not len(invites) > 0:    # don't accept duplicated invites
            invite.save()

    def remove_friend(self, profile_id):
        friend = UserProfile.objects.filter(id=profile_id)[0]
        self.friends.remove(friend)



class Invite(models.Model):
    inviter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='made_invites')
    invited = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_invites')

    def accept(self):
        self.invited.friends.add(self.inviter)
        self.inviter.friends.add(self.invited)
        self.delete()

    def __str__(self):
        return str(self.inviter)
from django.db import models
from django.contrib import messages
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

class ChurnPredictionModel(models.Model):
    # Define the fields for your model
    # You can adjust the fields based on your specific requirements
    logged_in_time = models.DateTimeField()
    activity_completion_time = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming you have a User model
    
    @classmethod
    def train_model(cls):
        # Step 1: Load and preprocess the data
        data = cls.objects.all().values('logged_in_time', 'activity_completion_time', ...)
        # Perform any necessary data cleaning and transformation steps
        
        # Step 2: Define churn
        data['churn'] = (data['logged_in_time'] < pd.Timedelta(hours=5)) & (data['activity_completion_time'] < pd.Timedelta(days=10))
        
        # Step 3: Feature engineering
        # Implement the feature engineering steps based on your requirements
        
        # Step 4: Label creation
        X = data.drop(['churn'], axis=1)
        y = data['churn']
        
        # Step 5: Model training
        model = RandomForestClassifier()
        model.fit(X, y)
        
        # Save the trained model to the database
        cls.objects.create(model_pickle=model)
    
    def predict_churn(self):
        # Load the trained model from the database
        model = self.model_pickle
        
        # Implement the logic to extract feature values from the instance
        new_user = pd.DataFrame({
            'logged_in_time': [self.logged_in_time],
            'activity_completion_time': [self.activity_completion_time],
            # Add other relevant features for the new user
        })
        
        churn_prediction = model.predict(new_user)
        
        if churn_prediction:
            # Churn is predicted
            user = self.user  # Assuming you have a User model
            user_churn_rate = self.calculate_churn_rate(user)
            self.record_churn_rate(user, user_churn_rate)
            
            if user_churn_rate < 0.75:
                # Churn prediction rate is below 75%, alert the user
                messages.warning(self.request, "Churn is predicted for user {}. Your churn prediction rate is {}%".format(user.username, user_churn_rate * 100))
        
        return churn_prediction
    
    @staticmethod
    def calculate_churn_rate(user):
        # Calculate the churn rate for the user based on their historical churn data
        churn_count = ChurnPredictionModel.objects.filter(user=user, churn=True).count()
        total_count = ChurnPredictionModel.objects.filter(user=user).count()
        
        if total_count == 0:
            return 0.0
        
        churn_rate = churn_count / total_count
        return churn_rate
    
    @staticmethod
    def record_churn_rate(user, churn_rate):
        # Update the churn rate for the user in the user model or any other relevant model
        user.churn_rate = churn_rate
        user.save()
    def get_absolute_url(self):
        return reverse("complete_task",kwargs={"id":self.id})

