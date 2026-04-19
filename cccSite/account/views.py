from google.oauth2 import id_token
from google.auth.transport import requests
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from PIL import Image

# If the user is not signed in, show the sign-in page.
# If they ARE signed in, redirect them to their account dashboard.
def signin(request):
    if request.session.get('rank', 0) == 0:
        return render(request, 'account/signin.html')
    else:
        return redirect("/account/")

# Handles signing out.
# If the user hits this URL with POST, flush the session.
# If they try GET (typing URL manually), just redirect safely.
def signout(request):
    if request.method == "POST":
        request.session.flush()
    return redirect(reverse("account:default"))

# Default account page.
# If not signed in, redirect to sign-in.
# Otherwise load the Member object and pass user info to the template.
def default(request):
    if request.session.get('rank', 0) == 0:
        return redirect(reverse("account:signin"))
    else:
        userInz = Member.objects.get(pk=request.session['user'])  # get user from session
        return render(request, 'account/myaccount.html', {
            'name': userInz.name,
            'email': userInz.email,
            'image': userInz.pic,
            'about': userInz.about,
        })

# Placeholder view for listing all accounts (not implemented yet)
def account_all(request):
    return HttpResponse("insert account view list here")

# View a specific account by primary key.
# If the user doesn't exist, redirect to default.
def account_view(request, want):
    if not want:
        return HttpResponse("Insert list view here")
    if not Member.objects.get(pk=want):
        return redirect(reverse("account:default"))
    viewInz = Member.objects.get(pk=want)

    # If logged in, load the current user.
    # Otherwise return an empty queryset.
    if request.session.get('rank', 0) != 0:
        userInz = Member.objects.get(request.session['user'])
    else:
        userInz = Member.objects.none()

# Allows members to edit their account info.
# Uses ManageForm to update the Member model.
def manage(request):
    if request.session.get('rank', 0) == 0:
        return redirect('/account/signin/')

    if request.method == "POST":
        userInz = Member.objects.get(pk=request.session['user'])
        form = ManageForm(request.POST, request.FILES, instance=userInz)

        # Save updated info if valid
        if form.is_valid():
            form.save()
            request.session['name'] = userInz.name  # update session name
            return redirect("/account/")
    else:
        # Load form with existing user data
        userInz = Member.objects.get(pk=request.session['user'])
        form = ManageForm(instance=userInz)

    return render(request, "account/manage.html", {'form': form})

# Google OAuth authentication endpoint.
# csrf_exempt is required because Google sends the POST request.
@csrf_exempt
def authG(request):
    # GET requests should not hit this endpoint; redirect safely.
    if request.method == "GET":
        return redirect("/account/")

    elif request.method == "POST":

        # Validate Google CSRF token
        csrf_tok_cookie = request.COOKIES.get('g_csrf_token')
        if not csrf_tok_cookie:
            return HttpResponse("Something went wrong, no csrf cookie")

        csrf_tok_body = request.POST.get('g_csrf_token')
        if not csrf_tok_body:
            return HttpResponse("Something went wrong, no csrf cookie from google")

        if csrf_tok_cookie != csrf_tok_body:
            return HttpResponse("Could not verify csrf")

        # Extract Google credential token
        tok = request.POST.get("credential")

        try:
            # Verify token with Google
            idinfo = id_token.verify_oauth2_token(
                tok,
                requests.Request(),
                "316865720473-94ccs1oka6ev4kmlv5ii261dirvjkja0.apps.googleusercontent.com"
            )

            # If this Google ID has never logged in before, create a new Member + GLogIn entry
            if not GLogIn.objects.filter(googleID=idinfo['sub']).exists():

                # Create a new Member using Google profile info
                userInz = Member.objects.create(
                    name=idinfo['given_name'],
                    email=idinfo['email']
                )

                # Link Google ID to the new Member
                gLogInz = GLogIn.objects.create(
                    googleID=idinfo['sub'],
                    referTo=userInz
                )

            else:
                # Existing Google login — load the linked Member
                gLogInz = GLogIn.objects.get(googleID=idinfo['sub'])
                userInz = gLogInz.referTo

            # Store user info in session
            request.session['rank'] = userInz.ranking
            request.session['user'] = userInz.pk
            request.session['name'] = userInz.name

        except ValueError:
            # Token invalid or verification failed
            return HttpResponse("Something went wrong, invalid credentials from Google (somehow)")

        # Successful login → redirect to account dashboard
        return redirect("/account/")

def google_info(request):
    # Load the logged-in Member object using the session
    if request.session.get('rank', 0) == 0:
        return redirect("/account/signin/")

    userInz = Member.objects.get(pk=request.session['user'])

    # Try to get the linked Google account (if any)
    google = None
    try:
        google = GLogIn.objects.get(referTo=userInz)
    except GLogIn.DoesNotExist:
        google = None

    return render(request, "account/google_info.html", {
        "name": userInz.name,
        "email": userInz.email,
        "google": google,
    })

def training_page(request):
    return render(request, "account/training_page.html")
