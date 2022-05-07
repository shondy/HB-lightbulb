"""Server for movie ratings app."""

from flask import Flask, render_template, request, flash, session, redirect
from model import connect_to_db, db, User, Idea, Vote, Comment

from jinja2 import StrictUndefined
import crud

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """View homepage."""

    return render_template("homepage.html")

@app.route("/ideas")
def ideas_per_page():
    """View all ideas with pagination."""

    page = int(request.args.get("page", "1"))
    per_page = int(request.args.get("per_page", "5"))

    # ideas = Idea.get_ideas_per_page(page, per_page)
    ideas_with_votes = crud.get_ideas_with_votes(session.get("user_id"), page, per_page)

    return render_template("all_ideas.html", ideas=ideas_with_votes, per_page=per_page)

@app.route("/ideas/<idea_id>")
def show_idea(idea_id):
    """Show details on a particular idea with all comments."""

    idea = Idea.get_by_id(idea_id)
    comments = Comment.get_by_idea_id(idea_id)

    return render_template("idea_details.html", idea=idea, comments=comments)


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
    """Handling the creation of a new user."""

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
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.")

        return redirect("/login")

    else:
        return render_template("users.html")

@app.route("/comments/<idea_id>", methods=['GET', 'POST'])
def create_comment(idea_id):
    """Create, update, read a comment."""

    if request.method == 'POST':
        """Create a new comment."""

        user = User.get_by_id(session["user_id"])
        idea = Idea.get_by_id(idea_id)
        description = request.json.get("description")
        
        comment = Comment.create(user, idea, description)
        db.session.add(comment)
        db.session.commit()
        
        return {
            "success": True, 
            "status": f"Your comment for idea {idea.idea_id} was added"}
    
    else:
        """Show template for creating a comment"""

        idea = Idea.get_by_id(idea_id)

        return render_template("comment_details.html", idea=idea, method="POST")

@app.route("/comments/<idea_id>/<comment_id>", methods=['GET', 'PUT'])
def edit_comment(idea_id, comment_id):

    if request.method == 'PUT':
        """Update a comment."""

        comment = Comment.get_by_id(comment_id)
        description = request.json.get("description")
        
        comment.description = description
        db.session.commit()
        
        return {
            "success": True, 
            "status": f"Your comment for idea {idea.idea_id} was added"}
    
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
    db.session.add(vote)
    db.session.commit()

    return {
        "success": True, 
        "status": f"Your vote for idea {idea.idea_id} was added"}

@app.route("/votes", methods=['DELETE'])
def delete_vote():
    """delete a vote."""

    idea_id = request.json.get("idea_id")
    user_id = session["user_id"]
    
    
    vote = Vote.get_by_user_id_and_idea_id(user_id, idea_id)
    db.session.delete(vote)
    db.session.commit()

    return {
        "success": True, 
        "status": f"Your vote for idea {idea_id} was deleted"}
  


# @app.route("/users/<user_id>")
# def show_user(user_id):
#     """Show details on a particular user."""

#     user = User.get_by_id(user_id)

#     return render_template("user_details.html", user=user)




# @app.route("/update_rating", methods=["POST"])
# def update_rating():
#     rating_id = request.json["rating_id"]
#     updated_score = request.json["updated_score"]
#     Rating.update(rating_id, updated_score)
#     db.session.commit()

#     return "Success"

# @app.route("/movies/<movie_id>/ratings", methods=["POST"])
# def create_rating(movie_id):
#     """Create a new rating for the movie."""

#     logged_in_email = session.get("user_email")
#     rating_score = request.form.get("rating")

#     if logged_in_email is None:
#         flash("You must log in to rate a movie.")
#     elif not rating_score:
#         flash("Error: you didn't select a score for your rating.")
#     else:
#         user = User.get_by_email(logged_in_email)
#         movie = Movie.get_by_id(movie_id)

#         rating = Rating.create(user, movie, int(rating_score))
#         db.session.add(rating)
#         db.session.commit()

#         flash(f"You rated this movie {rating_score} out of 5.")

#     return redirect(f"/movies/{movie_id}")


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
