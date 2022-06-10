"""Server for movie ratings app."""

from flask import Flask, render_template, request, flash, session, redirect, jsonify, abort, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from model import connect_to_db, db, User, Idea, Vote, Comment
from sqlalchemy import exc
from itsdangerous import URLSafeTimedSerializer

from jinja2 import StrictUndefined
import crud
import os
from utils import send_confirmation_email

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
app.jinja_env.undefined = StrictUndefined

client_id = os.environ['GOOGLE_CLIENT_ID']
client_secret = os.environ['GOOGLE_CLIENT_SECRET']

salt = os.environ['EMAIL_CONFIRMATION_SALT']


# A Blueprint object works similarly to a Flask application object, but it is not actually an application. 
# Rather it is a blueprint of how to construct or extend an application.
blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    scope=["profile", "email"],
    redirect_url="/login_google"
)
app.register_blueprint(blueprint, url_prefix="/login")

@app.route("/login_google")
def process_google_auth():
    """Handling user authorization through Google."""

    if google.authorized:
        user_info = google.get('/oauth2/v2/userinfo')
        if user_info.ok:
            user_info = user_info.json()
            user = User.get_by_email(user_info["email"])
            if not user:
                user = User.create_google_user(user_info["name"], user_info["email"])
                try:
                    db.session.add(user)
                    db.session.commit()
                except exc.SQLAlchemyError as err:
                    db.session.rollback()
                    abort(422)

            session["user_id"] = user.user_id

        else:
            flash("Cannot sign in with Google. Try again.")
        
        return redirect("/all-ideas")

@app.route("/login", methods=['GET', 'POST'])
def process_login():
    """Process user login."""

    if request.method == 'POST':
        email = request.json.get("email")
        password = request.json.get("password")
        user = User.get_by_email(email)

        # if user with this email doesn't exist in db or
        # if user has never created account but only authorized with googl or
        # if user hasn't yet confirmed the email or
        # if password isn't correct => abort
        if not user or user.google_sign_only or not user.verify_password(password):
            abort(400, "The email or password you entered was incorrect.")
        elif not user.email_confirmed:
            abort(400, "You have not activated your account.")
        # Log in user by storing the user's id in session
        session["user_id"] = user.user_id
        return jsonify({"success": True})

    else:
        return render_template("login.html")


@app.route("/logout")
def process_logout():
    """Process user logout."""

    session.pop('user_id')
    return redirect("/")


@app.route("/users", methods=['GET', 'POST'])
def join():
    """Handle creating of a new user."""

    if request.method == 'POST':
        username = request.json.get("username")
        email = request.json.get("email")
        password = request.json.get("password")

        user = User.get_by_email(email)

        if user and not user.google_sign_only:
            abort(400, f"This user already exists.")
        
        else:
            new_user = False
            if not user:
                # if its a new user
                new_user = True
                try:
                    user = User.create(username, email, password)
                except ValueError as err:
                    abort(400, err.args[0])

            else: 
                # if a user has already signed in with Google before using the same email, 
                # but never created a password => update user username, password, email_confirmation_sent_on,
                # and set google_sign_only to false
                try:
                    User.update_google_signed_to_unconfirmed(user.user_id, username, password)
                except ValueError as err:
                    abort(400, err.args[0])

            try:
                if new_user:
                    db.session.add(user)
                db.session.commit()

                send_confirmation_email(user.email)
                return jsonify({ 
                    "success": True,
                    "joined": user.user_id
                    })

            except exc.SQLAlchemyError as err:
                db.session.rollback()
                abort(422)

    else:
        return render_template("join.html")

@app.route("/confirm_email/<token>")
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt=salt, max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.')
        return redirect('/')
    
    user = User.get_by_email(email)
    
    if user.email_confirmed:
        flash('Account already confirmed. Please login.')
    else:
        User.confirm_email(user.user_id) 
        try:
            db.session.add(user)
            db.session.commit()
            flash('Thank you for confirming your email address!')
        except exc.SQLAlchemyError as err:
                db.session.rollback()
                abort(422)    
 
    return redirect('/')

@app.route("/")
def homepage():
    """View homepage."""

    return render_template("homepage.html")

@app.route("/all-ideas")
def ideas_per_page():
    """View all ideas with pagination."""

    page = int(request.args.get("page", "1"))
    perpage = int(request.args.get("perpage", "10"))

    search = request.args.get("search", "")
    sort = request.args.get("sort", "latest")

    ideas_with_votes = crud.get_ideas_with_votes_filtered(session.get("user_id"), search, sort, page, perpage)

    return render_template("ideas.html", 
    ideas=ideas_with_votes, 
    title="Ideas",
    search=search, 
    sort=sort, 
    perpage=perpage, 
    action="/all-ideas")

@app.route("/ideas", methods=['GET', 'POST'])
def create_idea():
    """handle creating an idea."""

    if request.method == 'POST':
        """Create a new idea."""
        if not session.get("user_id"):
            abort(400, "User did not login to the application.")

        user = User.get_by_id(session["user_id"])
        title = request.json.get("title")
        description = request.json.get("description")
        link = request.json.get("link")
        image = request.json.get("image")
        
        idea = Idea.create(user, title, description, link, image)
        print("idea==========================", idea)
        try:
            db.session.add(idea)
            db.session.commit()
            return jsonify({ 
                "success": True,
                "added": idea.idea_id
                })

        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)
    
    else:
        """Show template for creating an idea"""

        return render_template("idea_details.html", method="POST")

@app.route("/ideas/<idea_id>", methods=['GET', 'PUT'])
def edit_idea(idea_id):
    """Handle changing of an idea """

    idea = Idea.get_by_id(idea_id)

    if request.method == 'PUT':
        """Update an idea."""

        if not session.get("user_id") or idea.user_id != session["user_id"]:
            abort(400, "User did not login to the application.")

        title = request.json.get("title")
        description = request.json.get("description")
        link = request.json.get("link")
        image = request.json.get("image")

        Idea.update(idea_id, title, description, link, image)
  
        try:
            db.session.commit()
            return jsonify({ 
                "success": True,
                "updated": idea_id
                })

        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)

    else:
        """Show template for editing an idea."""

        return render_template("idea_details.html", idea=idea, method="PUT")

@app.route("/ideas/<idea_id>/comments")
def show_idea(idea_id):
    """Show details of an idea with all comments to this idea."""

    idea = Idea.get_by_id(idea_id)
    comments = Comment.get_by_idea_id(idea_id)
    idea_votes = crud.get_idea_votes(session.get("user_id"), idea_id)

    return render_template("idea_details_with_comments.html", idea=idea, comments=comments, idea_votes=idea_votes)


@app.route("/users/<user_id>")
def show_user(user_id):
    """Show user settings"""
    user = User.get_by_id(user_id)

    return render_template("user_settings.html", user=user)


@app.route("/users/<user_id>/details", methods=['PUT'])
def edit_user_details(user_id):
    """Update user details: username, description."""

    if not session.get("user_id") or int(user_id) != session["user_id"]:
        abort(400, "User did not login to the application.")

    username = request.json.get("username")
    description = request.json.get("description")
    try:
        user = User.update_details(user_id, username, description)
    except ValueError as err:
        abort(400, err.args[0])

    try:
        db.session.commit()
        return jsonify({ 
            "success": True,
            "updated": user_id
            })

    except exc.SQLAlchemyError as err:
        db.session.rollback()
        abort(422)

@app.route("/users/<user_id>/password", methods=['PUT'])
def edit_user_password(user_id):
    """Update user password."""

    if not session.get("user_id") or int(user_id) != session["user_id"]:
        abort(400, "User did not login to the application.")

    password = request.json.get("password")
    confirm_password = request.json.get("confirmPassword")

    try:
        user = User.update_password(user_id, password, confirm_password)
    except ValueError as err:
        abort(400, err.args[0])

    try:
        db.session.commit()
        return jsonify({ 
            "success": True,
            "updated": user_id
            })

    except exc.SQLAlchemyError as err:
        db.session.rollback()
        abort(422)

@app.route("/users/<user_id>/ideas")
def user_ideas(user_id):
    """Show all ideas created by user."""

    page = int(request.args.get("page", "1"))
    perpage = int(request.args.get("perpage", "10"))

    search = request.args.get("search", "")
    sort = request.args.get("sort", "latest")

    ideas_with_votes = crud.get_user_ideas_with_votes_filtered(user_id, session.get("user_id"), search, sort, page, perpage)
    user = User.get_by_id(user_id)

    most_voted_idea = crud.get_most_voted_user_idea(user_id)

    return render_template("ideas.html", 
    ideas=ideas_with_votes, 
    title="My ideas",
    user=user, 
    most_voted_idea=most_voted_idea, 
    search=search, 
    sort=sort,
    perpage=perpage,
    action = f"/users/{user_id}/ideas")


@app.route("/users/<user_id>/votes")
def user_votes(user_id):
    """Show all ideas user voted for."""

    page = int(request.args.get("page", "1"))
    perpage = int(request.args.get("perpage", "10"))

    search = request.args.get("search", "")
    sort = request.args.get("sort", "latest")

    ideas_with_votes = crud.get_voted_by_user_ideas_with_votes_filtered(user_id, search, sort, page, perpage)

    return render_template("ideas.html", 
    ideas=ideas_with_votes, 
    title="My votes",
    perpage=perpage, 
    search=search, 
    sort=sort,
    action=f"/users/{user_id}/votes")



@app.route("/comments/<idea_id>", methods=['GET', 'POST'])
def create_comment(idea_id):
    """handle creating a comment."""

    if request.method == 'POST':
        """Create a new comment."""
        if not session.get("user_id"):
            abort(400, "User did not login to the application.")

        user = User.get_by_id(session["user_id"])
        idea = Idea.get_by_id(idea_id)
        description = request.json.get("description")
        
        comment = Comment.create(user, idea, description)
        try:
            db.session.add(comment)
            db.session.commit()
            return {
                "success": True, 
                "added": comment.comment_id
                }

        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)
    
    else:
        """Show template for creating a comment"""

        idea = Idea.get_by_id(idea_id)

        return render_template("comment_details.html", idea=idea, method="POST")

@app.route("/comments/<idea_id>/<comment_id>", methods=['GET', 'PUT', 'DELETE'])
def edit_comment(idea_id, comment_id):
    """handle changing a comment."""

    comment = Comment.get_by_id(comment_id)

    if request.method == 'PUT':
        """Update a comment."""

        if not session.get("user_id") or comment.user_id != session["user_id"]:
            abort(400, "User did not login to the application.")

        description = request.json.get("description")
        Comment.update(comment_id, description)
  
        try:
            db.session.commit()
            return jsonify({ 
                "success": True,
                "updated": comment_id
            })
        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)

    elif request.method == 'DELETE':
        """Delete a comment."""

        if not session.get("user_id") or comment.user_id != session["user_id"]:
            abort(400, "User did not login to the application.")

        try:
            db.session.delete(comment)
            db.session.commit()
            return jsonify({ 
                "success": True,
                "deleted": comment_id
            })
        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)
        
    else:
        """Show template for editing a comment."""

        idea = Idea.get_by_id(idea_id)

        return render_template("comment_details.html", idea=idea, comment=comment, method="PUT")


@app.route("/votes", methods=['POST'])
def create_vote():
    """Create a vote."""

    idea_id = request.json.get("idea_id")
    idea = Idea.get_by_id(idea_id)
    if not session.get("user_id"):
        abort(400, "User did not login to the application.")

    user_id = session["user_id"]
    user = User.get_by_id(user_id)
    
    vote = Vote.create(user, idea)
    try:
        db.session.add(vote)
        db.session.commit()
        return jsonify({ 
            "success": True,
             "added": vote.vote_id
        })
    except exc.SQLAlchemyError as err:
        db.session.rollback()
        abort(422)


@app.route("/votes", methods=['DELETE'])
def delete_vote():
    """delete a vote."""

    idea_id = request.json.get("idea_id")
    if not session.get("user_id"):
        abort(400, "User did not login to the application.")

    user_id = session["user_id"]
    
    vote = Vote.get_by_user_id_and_idea_id(user_id, idea_id)
    vote_id = vote.vote_id

    try:
        db.session.delete(vote)
        db.session.commit()
        return jsonify({ 
            "success": True,
             "deleted": vote_id
        })
    except exc.SQLAlchemyError as err:
        db.session.rollback()
        abort(422)

@app.errorhandler(400)
def custom400(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": error.description
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

# @app.errorhandler(400)
# def bed_request(error):
#     return jsonify({
#         "success": False,
#         "error": 400,
#         "message": "bed request"
#     }), 400

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


if __name__ == "__main__":
    connect_to_db(app)
    # app.run('0.0.0.0', debug=True, port=8100, ssl_context=(
    #     'certificates/server.crt', 
    #     'certificates/server.key'))
    # app.run(host="0.0.0.0", debug=True)
    app.run()
