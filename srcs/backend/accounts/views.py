from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from .models import OauthTokenResponse
import os
import requests
import json
import urllib.parse

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
    return render(request, 'registration/register.html', {'form': form})

def custom_login(request):
    if request.method != 'POST':
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({'success': True, 'username': user.username}, status=201)
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

# def oauth_token(request):
#     is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
#     if is_ajax:
#         # data = {"test": "reached oauth_token"}
#         # return JsonResponse(data)
#         if request.method == 'POST':
#             params = {
#                 'client_id': os.getenv('FTAPI_UID'),
#                 'redirect_uri': 'https://localhost/home',
#                 'response_type': 'code',
#                 'scope': 'public',
#                 'state': 'qwerty',
#             }
#             base_url = 'https://api.intra.42.fr/oauth/authorize?'
#             query_string = urllib.parse.urlencode(params)
#             url = base_url + query_string
#             return HttpResponseRedirect(url)
#             # response = requests.post(url)
#             # Print the response headers
#             # print(f"Headers: {response.headers}")

#             # # Print the response content
#             # print(f"Content: {response.text}")

#             # # Print the response JSON (if it exists)
#             # if 'application/json' in response.headers.get('Content-Type', ''):
#             #     print(f"JSON: {response.json()}")
#             # if response.status_code == 200:
#             #     return JsonResponse({'success': True})
#             # else:
#             #     return JsonResponse({'success': False, 'error': 'OAuth request failed'}, status=400)
#         else:
#             return HttpResponseBadRequest('Invalid request mewthod')
#     else:
#         return HttpResponseBadRequest('Invalid request method')

def oauth_token(request):
    code = request.GET.get('code')

    if code is None:
        return JsonResponse({'success': False, 'error': 'OAuth no code'}, status=400)
    return JsonResponse({'success': True, 'code': code})
    data = {
        'grant_type': 'authorization_code',
        'client_id': os.getenv('FTAPI_UID'),
        'client_secret': os.getenv('FTAPI_SECRET'),
        'code': code,
        'redirect_uri': 'https://localhost/home',
    }

    response = requests.post('https://api.intra.42.fr/oauth/token', data=data)

    if response.status_code == 200:
        access_token = response.json().get('access_token')
        # Save the access token in the session or database
        request.session['access_token'] = access_token
        return HttpResponse('Authorization successful.')
    else:
        return HttpResponse('Error: Authorization failed.', status=400)