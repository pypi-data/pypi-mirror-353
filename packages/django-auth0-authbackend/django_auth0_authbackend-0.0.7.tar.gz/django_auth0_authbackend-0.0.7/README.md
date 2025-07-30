# django-auth0-auth

Authentication backend for Django with Auth0. As of June 2025, all of
the libraries that I saw for Django Auth0 target old versions of Django,
we\'ll start this by supporting version 5+ and python 3.11+ (3.10 only
has 1 year of life). Also, some of these don\'t actually subclass
Django\'s `AuthBackend`{.verbatim} and implement a login system that is
more \"beside\" Django than integrated with it. Because this is fully
integrated, we can use Django\'s built-in `@login_required`{.verbatim}
decorator and it\'s auth Mixins.

This project is not affiliated with Auth0.

The names are slightly confusing because there are a lot of one-off
projects (like this one) on PyPI that attempt the same thing. The repo
name here is `django-auth0-auth`{.verbatim}, the pypi name is
`django-auth0-authbackend`{.verbatim}, and the importable package is
`auth0`{.verbatim}. The installation instructions below reflect these
names.

## Installation

Install the package from PyPI:

    pip install django-auth0-authbackend

## Usage

Take a look at the sample app provided in `sample/`{.verbatim} to see
how it\'s used in a MWE. There are only a few steps. First, include the
app in your apps in your Django settings:

    INSTALLED_APPS = [
        ...,
        "auth0",
    ]

Next, include the auth settings and auth backend (also in your Django
settings):

    AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
    AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
    AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE")

    AUTHENTICATION_BACKENDS = [
        "auth0.backend.Auth0Backend",
    ]

Finally, include the urls in your project `urls.py`{.verbatim}:

    from django.urls import path, include

    urlpatterns = [
        ...,
        path("auth0/", include("auth0.urls")),
    ]

## Running the sample app

First, create an auth0 application.

Set up python however you prefer, I\'ll use a virtual env:

    ~/.pyenv/versions/3.11.10/bin/python -m venv .venv
    source .venv/bin/activate
    pip install .

Running the sample app, we can do:

    export AUTH0_CLIENT_ID=...
    export AUTH0_CLIENT_SECRET=...
    export AUTH0_DOMAIN=...
    export AUTH0_AUDIENCE=...
    python manage.py migrate
    python manage.py runserver

Go to <http://localhost:8000/auth0> and log in!

## Next steps

-   [x] Test that it works with the sample app (create an auth0 account
    to test)
-   [ ] Run through genAI to look for general improvements: is all the
    logic we have in the views/index the right place for this?
-   [x] Add pre-commit code checks
-   [x] Add automated release via github action
-   [x] Flesh out user documentation here in README
-   [ ] Add automated tests
-   [ ] Profit
