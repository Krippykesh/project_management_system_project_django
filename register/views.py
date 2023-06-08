import random
from django.shortcuts import render,redirect
from django.contrib.auth import login
from django.shortcuts import redirect
from projects.models import Task
from .models import UserProfile
from .models import Invite
from .forms import RegistrationForm
from .forms import CompanyRegistrationForm
from .forms import ProfilePictureForm
from .models import ChurnPredictionModel

def complete_task(request):
    print('hey')
    if request.method == 'POST':
        print('is post')
        # Extract the necessary data from the form
        logged_in_time = request.POST['logged_in_time']
        activity_completion_time = request.POST['activity_completion_time']
        user = request.user  # Assuming you have a User model
        
        # Create a new ChurnPredictionModel instance
        churn_prediction = ChurnPredictionModel.objects.create(
            logged_in_time=logged_in_time,
            activity_completion_time=activity_completion_time,
            user=user
        )
        
        # Predict churn and record churn rate
        churn_prediction.predict_churn()
        print('churn predicted')
        
        return redirect('task_completed')  # Redirect to a success page after completing the task
    
    return render(request, 'register/task_completion.html')

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        context = {'form':form}
        if form.is_valid():
            user = form.save()
            created = True
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            context = {'created' : created}
            return render(request, 'register/reg_form.html', context)
        else:
            return render(request, 'register/reg_form.html', context)
    else:
        form = RegistrationForm()
        context = {
            'form' : form,
        }
        return render(request, 'register/reg_form.html', context)


def usersView(request):
    users = UserProfile.objects.all()
    tasks = Task.objects.all()
    context = {
        'users': users,
        'tasks': tasks,
    }
    return render(request, 'register/users.html', context)

def user_view(request, profile_id):
    user = UserProfile.objects.get(id=profile_id)
    context = {
        'user_view' : user,
    }
    return render(request, 'register/user.html', context)


def profile(request):
    if request.method == 'POST':
        img_form = ProfilePictureForm(request.POST, request.FILES)
        print('PRINT 1: ', img_form)
        context = {'img_form' : img_form }
        if img_form.is_valid():
            img_form.save(request)
            updated = True
            context = {'img_form' : img_form, 'updated' : updated }
            return render(request, 'register/profile.html', context)
        else:
            return render(request, 'register/profile.html', context)
    else:
        img_form = ProfilePictureForm()
        context = {'img_form' : img_form }
        return render(request, 'register/profile.html', context)


def newCompany(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        context = {'form':form}
        if form.is_valid():
            form.save()
            created = True
            form = CompanyRegistrationForm()
            context = {
                'created' : created,
                'form' : form,
                       }
            return render(request, 'register/new_company.html', context)
        else:
            return render(request, 'register/new_company.html', context)
    else:
        form = CompanyRegistrationForm()
        context = {
            'form' : form,
        }
        return render(request, 'register/new_company.html', context)


def invites(request):
    return render(request, 'register/invites.html')


def invite(request, profile_id):
    profile_to_invite = UserProfile.objects.get(id=profile_id)
    logged_profile = get_active_profile(request)
    if not profile_to_invite in logged_profile.friends.all():
        logged_profile.invite(profile_to_invite)
    return redirect('core:index')


def deleteInvite(request, invite_id):
    logged_user = get_active_profile(request)
    logged_user.received_invites.get(id=invite_id).delete()
    return render(request, 'register/invites.html')


def acceptInvite(request, invite_id):
    invite = Invite.objects.get(id=invite_id)
    invite.accept()
    return redirect('register:invites')

def remove_friend(request, profile_id):
    user = get_active_profile(request)
    user.remove_friend(profile_id)
    return redirect('register:friends')


def get_active_profile(request):
    user_id = request.user.userprofile_set.values_list()[0][0]
    return UserProfile.objects.get(id=user_id)


def friends(request):
    if request.user.is_authenticated:
        user = get_active_profile(request)
        friends = user.friends.all()
        context = {
            'friends' : friends,
        }
    else:
        users_prof = UserProfile.objects.all()
        context= {
            'users_prof' : users_prof,
        }
    return render(request, 'register/friends.html', context)
from django.shortcuts import render
from .forms import ChurnPredictionForm
from .models import ChurnPredictionModel

def churn_prediction(request):
    
    dhatime=["9:00 AM","9:30 AM","10:00 AM","10:30 AM","11:00 AM","11:30 AM","12:00 PM","12:30 PM","1:00 PM","1:30 PM","2:00 PM","2:30 PM","3:00 PM","3:30 PM","4:00 PM","4:30 PM","5:00 PM","5:30 PM","6:00 PM","6:30 PM","7:00 PM","7:30 PM"]
    r_index=random.randint(0, len(dhatime)-1)    
    
    random_logged_in_time = dhatime[r_index]  # Example: Random logged-in time
    random_completion_duration = random.randint(1, 29)  # Example: Random completion duration less than 30

    return render(request, 'register/churn_prediction.html', {
        'random_logged_in_time': random_logged_in_time,
        'random_completion_duration': random_completion_duration,
    })

def predict_churn(logged_in_time, activity_completion_time):
    # Placeholder code for churn prediction
    # Replace this with your actual implementation
    
    # Perform some calculations or data analysis
    # to predict churn based on the given input
    
    # For example, you can return a random churn prediction percentage
    churn_prediction = random.uniform(0, 100)
    
    return churn_prediction

from .models import ChurnPredictionModel

