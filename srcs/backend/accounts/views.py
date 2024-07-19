from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.http import JsonResponse

# Create your views here.


def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration form.
        # If we’re not responding to a POST request, we make an instance of
        # CustomUserCreationForm with no initial data
        form = CustomUserCreationForm()
    else:
        # Process completed form.
        # Make an instance of CustomUserCreationForm based on the submitted data
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            """ If the submitted data is valid, we call the form's save() 
            method to save the username and the hash of the password to the database """
            new_user = form.save()
            """ Log the user in and then redirect to home page. The save() method returns
            the newly created user object, which we assign to new_user. When the user's 
            information is saved, we log them in by calling the login() function with 
            the request and new_user objects, which creates a valid session for the new user """
            login(request, new_user)
            # Assign the value of 'redirect_url' from POST data to the variable 'redirect_url'.
            # If 'redirect_url' does not exist in POST data, use '/' as the default value.
            redirect_url = request.POST.get('redirect_url', '/')
            return JsonResponse({'success': True, 'redirect': redirect_url, 'username': new_user.username}, status=201)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    # Display a blank or invalid form.
    return render(request, 'registration/register.html', {'form': form})

def custom_login(request):
    if request.method != 'POST':
        form = CustomAuthenticationForm()
    else:
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            redirect_url = request.POST.get('redirect_url', '/')
            return JsonResponse({'success': True, 'redirect': redirect_url, 'username': user.username}, status=201)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    # Display a blank or invalid form.
    return render(request, 'registration/login.html', {'form': form})

def custom_logout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
