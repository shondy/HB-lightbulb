"""Server for movie ratings app."""

from flask import Flask, render_template, request, flash, session, redirect, jsonify, abort
from model import connect_to_db, db, User, Idea, Vote, Comment
from sqlalchemy import exc

from jinja2 import StrictUndefined
import crud

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """View homepage."""

    return render_template("homepage.html")

@app.route("/all-ideas")
def ideas_per_page():
    """View all ideas with pagination."""

    page = int(request.args.get("page", "1"))
    per_page = int(request.args.get("per_page", "5"))

    # ideas = Idea.get_ideas_per_page(page, per_page)
    ideas_with_votes = crud.get_ideas_with_votes(session.get("user_id"), page, per_page)

    return render_template("all_ideas.html", ideas=ideas_with_votes, per_page=per_page)

@app.route("/ideas", methods=['GET', 'POST'])
def create_idea():
    """handle creating an idea."""

    if request.method == 'POST':
        """Create a new idea."""

        user = User.get_by_id(session["user_id"])
        title = request.form.get("title")
        description = request.form.get("description")
        link = request.form.get("link")
        
        idea = Comment.create(user, title, description, link)
        try:
            db.session.add(idea)
            db.session.commit()
            flash(f"Your idea was created!")
            return redirect("/all-ideas")

        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)
    
    else:
        """Show template for creating an idea"""

        return render_template("idea_details.html")

@app.route("/ideas/<idea_id>", methods=['GET', 'PUT'])
def edit_idea(idea_id):
    """Handling changing an idea """

    idea = Idea.get_by_id(idea_id)

    if request.method == 'PUT':
        """Update an idea."""

        title = request.form.get("title")
        description = request.form.get("description")
        link = request.form.get("link")

        idea.title = title
        idea.description = description
        idea.link = link
  
        try:
            db.session.commit()
            return redirect(f"/ideas/{idea_id}/comments")
        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)

    else:
        """Show template for editing an idea."""

        return render_template("idea_details.html", idea=idea)

@app.route("/ideas/<idea_id>/comments")
def show_idea(idea_id):
    """Show details on a particular idea with all comments."""

    idea = Idea.get_by_id(idea_id)
    comments = Comment.get_by_idea_id(idea_id)

    return render_template("idea_details_with_comments.html", idea=idea, comments=comments)


@app.route("/login", methods=['GET', 'POST'])
def process_login():
    """Process user login."""

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.get_by_email(email)
        print("user--------------->", user)
        if not user or user.password != password:
            flash("The email or password you entered was incorrect.")
            return redirect("/login")
        
        # Log in user by storing the user's email in session
        session["user_id"] = user.user_id
        flash(f"Welcome back, {user.username}!")

        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def process_logout():
    """Process user logout."""

    session.pop('user_id')
    return redirect("/")
    


@app.route("/users", methods=['GET', 'POST'])
def register_user():
    """Handle creating of a new user."""

    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.get_by_username(username)
        if user:
            flash(f"Username {username} is already taken. Try again.")
            return redirect("/users")

        user = User.get_by_email(email)
        if user:
            flash(f"Accont with email {email} already exists. Try again.")
            return redirect("/users")
        
        user = User.create(username, email, password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created! Please log in.")
            return redirect("/login")

        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)

    else:
        return render_template("users.html")

@app.route("/comments/<idea_id>", methods=['GET', 'POST'])
def create_comment(idea_id):
    """handle creating a comment."""

    if request.method == 'POST':
        """Create a new comment."""

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

        description = request.json.get("description")
        comment.description = description
  
        try:
            db.session.commit()
            return jsonify({ 
                "success": True,
                "udated": comment.comment_id
            })
        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)

    elif request.method == 'DELETE':
        """Delete a comment."""

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
    user_id = session["user_id"]
    
    
    vote = Vote.get_by_user_id_and_idea_id(user_id, idea_id)
    print("vote=======================", vote)
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

@app.errorhandler(400)
def bed_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bed request"
    }), 400

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
    app.run(host="0.0.0.0", debug=True)
