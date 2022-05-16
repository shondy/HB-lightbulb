"""Server for movie ratings app."""

from flask import Flask, render_template, request, flash, session, redirect, jsonify, abort
from model import connect_to_db, db, User, Idea, Vote, Comment
from sqlalchemy import exc

from jinja2 import StrictUndefined
import crud
import os

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
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
        title = request.json.get("title")
        description = request.json.get("description")
        link = request.json.get("link")
        
        idea = Idea.create(user, title, description, link)
        try:
            db.session.add(idea)
            db.session.commit()
            return jsonify({ 
                "success": True,
                "idea_id": idea.idea_id
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

    if request.method == 'PUT':
        """Update an idea."""

        title = request.json.get("title")
        description = request.json.get("description")
        link = request.json.get("link")

        Idea.update(idea_id, title, description, link)

        idea.title = title
        idea.description = description
        idea.link = link
  
        try:
            db.session.commit()
            return jsonify({ 
                "success": True,
                "idea_id": idea_id
                })

        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)

    else:
        """Show template for editing an idea."""

        idea = Idea.get_by_id(idea_id)

        return render_template("idea_details.html", idea=idea, method="PUT")

@app.route("/ideas/<idea_id>/comments")
def show_idea(idea_id):
    """Show details of an idea with all comments to this idea."""

    idea = Idea.get_by_id(idea_id)
    comments = Comment.get_by_idea_id(idea_id)

    return render_template("idea_details_with_comments.html", idea=idea, comments=comments)


@app.route("/login", methods=['GET', 'POST'])
def process_login():
    """Process user login."""

    if request.method == 'POST':
        email = request.json.get("email")
        password = request.json.get("password")
        user = User.get_by_email(email)
    
        if not user or not user.verify_password(password):
            abort(400, "The email or password you entered was incorrect.")
        
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
def register_user():
    """Handle creating of a new user."""

    if request.method == 'POST':
        username = request.json.get("username")
        email = request.json.get("email")
        password = request.json.get("password")
        print("================", username)

        try:
            user = User.create(username, email, password)
        except ValueError as err:
            abort(400, err.args[0])
        
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({ 
                "success": True,
                "added": user.user_id
                })

        except exc.SQLAlchemyError as err:
            db.session.rollback()
            abort(422)

    else:
        return render_template("user_details.html", method='POST')

@app.route("/users/<user_id>", methods=['GET', 'PUT'])
def edit_user(user_id):
    """Handle user info."""

    user = User.get_by_id(user_id)

    if request.method == 'PUT':
        """Update profile info of a user"""

        username = request.json.get("username")
        email = request.json.get("email")
        password = request.json.get("password")
        confirm_password = request.json.get("confirmPassword")

        try:
            user = User.update(user_id, username, email, password, confirm_password)
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
        
    else:
        """Show user info, user ideas and ideas voted by the user"""
        return render_template("user_details.html", method='PUT', user=user)

@app.route("/users/<user_id>/ideas")
def user_ideas(user_id):
    """Show all ideas created by user."""

    page = int(request.args.get("page", "1"))
    per_page = int(request.args.get("per_page", "5"))

    ideas_with_votes = crud.get_user_ideas_with_votes(user_id, page, per_page)

    return render_template("user_ideas.html", ideas=ideas_with_votes, per_page=per_page)
    

@app.route("/users/<user_id>/votes")
def user_votes(user_id):
    """Show all ideas user voted for."""

    page = int(request.args.get("page", "1"))
    per_page = int(request.args.get("per_page", "5"))

    ideas_with_votes = crud.get_voted_by_user_ideas_with_votes(user_id, page, per_page)

    return render_template("user_votes.html", ideas=ideas_with_votes, per_page=per_page)



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

    if request.method == 'PUT':
        """Update a comment."""

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

        comment = Comment.get_by_id(comment_id)

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
        comment = Comment.get_by_id(comment_id)

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
    app.run(host="0.0.0.0", debug=True)
