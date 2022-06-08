# Lightbulb

Lightbulb is a collaboration application for sharing and discussing project ideas. With Lightbulb users can look through project ideas and comments to them, search and sort project ideas. Authorized users can also create project ideas, add comments and vote for project ideas, receive email notifications about added comments to their ideas.


## Deployment
https://ridethrift.herokuapp.com/

*Please note the "request a ride" feature is for proof of concept only;
requests have been set to sandbox mode.

## Contents
* [Tech Stack](#technologies)
* [Features](#features)
* [Installation](#install)
* [About Me](#aboutme)

## <a name="technologies"></a>Technologies
- Python
- Flask
- SQLAlchemy
- Jinja2
- HTML
- CSS
- Javascript
- AJAX
- JSON
- Bootstrap
- Python unittest module

## <a name="features"></a>Features

Search for ideas by name and sorting of ideas by modification date, number votes or relevance. User account registration not required. <br />
Flask-msearch library - a full text search extension of Flask - was used for search.

![Ideas Search-sort Logged out](/static/img/_readme-img/search-sort.gif)

Look through ideas of certain user. User account registration not required.

![Users Ideas Logged out](/static/img/_readme-img/users-ideas.png)

Create an account or sign in with Google account to be able to add/edit an idea, add/edit/delete comment, vote for ideas.

![Create account Logged out](/static/img/_readme-img/create-account.png)

For activating an account user will be sent an email with a unique confirmation link. A link is generted using URLSafeSerializer from ItsDangerous.

![Confirm email Logged out](/static/img/_readme-img/confirm-email.png)

Log in to the created account or sign in with Google account

![Login](/static/img/_readme-img/login.png)

Add and edit ideas.

![Add idea Logged in](/static/img/_readme-img/change-idea.gif)

Vote for ideas.

![Voting Logged in](/static/img/_readme-img/voting.gif)

Add, edit, delete comments.

![Change comment Logged in](/static/img/_readme-img/change-comment.gif)

Receive email notifications about added/edited comment to user's ideas.

![Email notification](/static/img/_readme-img/email-notification.png)

Manage user account: edit user settings, look through user ideas and ideas user voted for.  

![Settings](/static/img/_readme-img/settings.gif)


## <a name="install"></a>Installation

To run Lightbulb:

Install PostgreSQL and Python 3.9

Clone or fork this repo:

```
https://github.com/shondy/HB-lightbulb
```

Create and activate a virtual environment inside your Lightbulb directory:

```
virtualenv env
source env/bin/activate
```

Install the dependencies:

```
pip install -r requirements.txt
```

[Create credentials](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid) to integrate Google Sign-In into Lightbulb app.

Save your credentials in a file called <kbd>secrets.sh</kbd> using this format:

```
export GOOGLE_CLIENT_ID="YOUR_KEY_HERE"
export GOOGLE_CLIENT_SECRET="YOUR_KEY_HERE"
export OAUTHLIB_INSECURE_TRANSPORT="YOUR_KEY_HERE"
export OAUTHLIB_RELAX_TOKEN_SCOPE="YOUR_KEY_HERE"

```
Also add to <kbd>secrets.sh</kbd>:
- secret key for flask app 
- salt that will be used in user's email encryption to create URL for confirmation of user's email address.
- password of Lightbulb email address that will be used to send notifications to users

```
export APP_SECRET_KEY="YOUR_KEY_HERE"
export NOTIFICATION_PASSWORD="YOUR_KEY_HERE"
export EMAIL_CONFIRMATION_SALT="YOUR_KEY_HERE"
```

Source your keys from your secrets.sh file into your virtual environment:

```
source secrets.sh
```

Set up the database:

```
createdb ideas
python3 model.py
```

To seed database with demo data:

```
python3 seed_database.py
```

Run the app:

```
python3 server.py
```

You can now navigate to 'localhost:5000/' to access Lightbulb.

## <a name="aboutme"></a>About Me
Lightbulb was created by Olga Tarasova. Learn more about the developer on [LinkedIn](https://www.linkedin.com/in/olga-tarasova-shondy).
```