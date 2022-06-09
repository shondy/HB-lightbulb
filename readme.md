# Lightbulb

**Lightbulb** is a collaboration application for sharing and discussing project ideas. With Lightbulb users can look through project ideas and comments to them, search and sort project ideas. Lightbulb has two types of  authorization: by creating an account and by signing in with a Google account. 
Authorized users can create and update project ideas, create, update and delete comments, vote for project ideas.
Also authorized users can change their settings, look through their ideas and votes, receive email notifications about added comments to their ideas.


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
- Google Sign-In API

## <a name="features"></a>Features
- Look through all ideas, search for ideas by name and sorting of ideas by modification date, number votes or relevance. 
User account registration is not required. <br />
To search for ideas I used msearch Flask extension to implement full-text search functionality.

![Search and sort ideas](/static/img/_readme-img/search-sort.gif)

- Look through idea details and commennts to an idea. User account registration is not required.

- Look through ideas of certain user. User account registration is not required.

![User's ideas](/static/img/_readme-img/users-ideas.png)

- Create an account or sign in with Google account to be able to create/update ideas, create/update/delete comments, vote for ideas.

![Create an account](/static/img/_readme-img/create-account.png)

For activating an account user will be sent an email with a unique confirmation link. A link is generted using URLSafeSerializer from ItsDangerous.

![Confirm an email](/static/img/_readme-img/confirm-email.png)

- Log in to the created account or sign in with Google account

![Login](/static/img/_readme-img/login.png)

- Create and update ideas (for authorized users).

![Add an idea](/static/img/_readme-img/change-idea.gif)

- Vote for ideas (for authorized users).

![Voting](/static/img/_readme-img/voting.gif)

- Create, update and delete comments (for authorized users).

![Change a comment](/static/img/_readme-img/change-comment.gif)

- Receive email notifications about added/edited comments to user's ideas.

![Email notification](/static/img/_readme-img/email-notification.png)

- Manage user account: edit user settings, look through user ideas and votes.

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

You can now navigate to 'localhost:5000/' to access Lightbulb app.

## <a name="aboutme"></a>About Me
Lightbulb was created by Olga Tarasova. Learn more about the developer on [LinkedIn](https://www.linkedin.com/in/olga-tarasova-shondy).
```