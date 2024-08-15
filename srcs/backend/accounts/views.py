from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.http import JsonResponse
import os
import requests
import json
from urllib.parse import urlencode, unquote, quote

# Create your views here.

login_42_params = {
    'client_id': os.getenv('FTAPI_UID'),
    'redirect_uri': os.getenv('FTAPI_REDIR_URL'),
    'response_type': 'code',
    'scope': 'public',
    'state': f'qwerty|{quote("https://localhost")}', # include redirect url to frontend
}
login_42_url = f"https://api.intra.42.fr/oauth/authorize?{urlencode(login_42_params)}"

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
    context = {
        'form': form,
        'form_title': 'REGISTER',
        'form_action': '/accounts/register/',
        'form_button_text': 'REGISTER',
        'alt_action': 'OR LOGIN',
        'alt_action_url': '/accounts/login/',
        'login_42_url': login_42_url,
    }
    return render(request, 'registration/form.html', context)

def custom_login(request):
    if request.method != 'POST':
        form = CustomAuthenticationForm()
    else:
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            redirect_url = request.POST.get('redirect_url', '/')
            return JsonResponse({'success': True, 'redirect': redirect_url, 'username': user.username})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    # Display a blank or invalid form.
    context = {
        'form': form,
        'form_title': 'LOGIN TO PLAY TOURNAMENTS',
        'form_action': '/accounts/login/',
        'form_button_text': 'LOGIN',
        'alt_action': 'OR REGISTER',
        'alt_action_url': '/accounts/register/',
        'login_42_url': login_42_url,
    }
    return render(request, 'registration/form.html', context)

def custom_logout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

"""
The oauth_token view is used to authenticate users with the 42 API
and log them in to the application. The view receives a code from the
42 API and uses it to get an access token. The access token is then used
to get the user's login, i.e. username from the 42 API. If the user exists in the
database, they are logged in. If the user does not exist, a new user is created
"""
def oauth_token(request):
    code = request.GET.get('code')
    if code is None:
        return redirect('/accounts/oauth_error/?from=oauth_token')
    data = {
        'grant_type': 'authorization_code',
        'client_id': os.getenv('FTAPI_UID'),
        'client_secret': os.getenv('FTAPI_SECRET'),
        'code': code,
        'redirect_uri': os.getenv('FTAPI_REDIR_URL'),
    }
    response = requests.post('https://api.intra.42.fr/oauth/token', data=data)
    if response.status_code == 200:
        # Use the redirect url to frontend stored in state
        state = request.GET.get('state')
        if not state:
            return redirect('/accounts/oauth_error/?from=oauth_token')
        # Split the state to extract the redirect url
        state_parts = state.split('|')
        if len(state_parts) < 2:
            return redirect('/accounts/oauth_error/?from=oauth_token')
        redirect_url = unquote(state_parts[1])

        access_token = response.json().get('access_token')
        # Save the access token in the session or database
        request.session['access_token'] = access_token
        # Use the access token to get the user info
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
        user_login = user_info_response.json().get('login')
        # Get the user model
        User = get_user_model()

        # Check if a user with the given username exists
        try:
            user = User.objects.get(username=user_login)
        except User.DoesNotExist:
            # If the user doesn't exist, create a new user
            # Note: You should set an unusable password for the user since
            # the password is not used in the OAuth flow
            user = User.objects.create_user(username=user_login)
            print(f"Creating new user: {user.username}")
            user.set_unusable_password()
            user.save()

        # Log the user in
        login(request, user)

        return redirect(redirect_url)
    else:
        return redirect('/accounts/oauth_error/?from=oauth_token')

"""
The oauth_error view handles the display of an OAuth error message.
It checks if the request is originated from the 'oauth_token' function.
If the request comes from 'oauth_token', it returns a JSON response with an error message.
Otherwise, it renders an HTML error page.
"""
def oauth_error(request):
    from_param = request.GET.get('from')
    if from_param == 'oauth_token':
        return JsonResponse({'success': False, 'error': '42 Authorization Error'}, status=400)
    else:
        return render(request, 'registration/oauth_error.html')