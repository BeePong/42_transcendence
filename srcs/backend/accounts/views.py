from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse

# Create your views here.


def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration form.
        # If we’re not responding to a POST request, we make an instance of
        # UserCreationForm with no initial data
        form = UserCreationForm()
    else:
        # Process completed form.
        # Make an instance of UserCreationForm based on the submitted data
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            """ If the submitted data is valid, we call the form's save() 
            method to save the username and the hash of the password to the database """
            new_user = form.save()
            """ Log the user in and then redirect to home page. The save() method returns
            the newly created user object, which we assign to new_user. When the user's 
            information is saved, we log them in by calling the login() function with 
            the request and new_user objects, which creates a valid session for the new user """
            login(request, new_user)
            return JsonResponse({'success': True, 'username': new_user.username}, status=201)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'registration/register.html', context)

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({'success': True, 'username': user.username}, status=201)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
