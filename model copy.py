"""Models for movie ratings app."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()


class User(db.Model):
    """A user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    # ratings = a list of Rating objects

    def __repr__(self):
        return f"<User user_id={self.user_id} username={self.username} email={self.email}>"

    @classmethod
    def create(cls, email, username, password):
       """Create and return a new user."""

       return cls(email=email, username=username, password=password)

    @classmethod
    def get_by_id(cls, user_id):
        """Return a user by primary key."""

        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email):
        """Return a user by email."""

        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_username(cls, username):
        """Return a user by username."""

        return cls.query.filter_by(username=username).first()


    @classmethod
    def all_users(cls):
        return cls.query.all()


class Idea(db.Model):
    """An idea."""

    __tablename__ = "ideas"

    idea_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200), nullable=True)
    modified = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    user = db.relationship("User", backref="ideas")


    def __repr__(self):
        return f"<Idea idea_id={self.idea_id} title={self.title}>"

    @classmethod
    def create(cls, user, title, description, link = None, modified=None):
        """Create and return a new idea."""

        if not modified:
            modified = datetime.now()
            
        return cls(
            user=user,
            title=title,
            description=description,
            link=link,
            modified=modified
            )
        
    @classmethod
    def update(cls, idea_id, new_title, new_description):
        """ Update a idea given idea_id and the updated title and description. """
        idea = cls.query.get(idea_id)
        idea.title = new_title
        idea.description = new_description
        idea.modified = datetime.now()

    @classmethod
    def all_ideas(cls):
        """Return all ideas."""

        return cls.query.all()

    @classmethod
    def get_ideas_per_page(cls, page, per_page):
        """Return all ideas on the page."""

        return cls.query.paginate(page, per_page, error_out = False)

    @classmethod
    def get_by_id(cls, idea_id):
        """Return an idea by primary key."""

        return cls.query.get(idea_id)

class Vote(db.Model):
    """A vote for an idea left by a user."""

    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint('user_id', 'idea_id'),)

    vote_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    modified = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.idea_id"))

    user = db.relationship("User", backref="votes")
    idea = db.relationship("Idea", backref="votes")

    def __repr__(self):
        return f"<Vote vote_id={self.vote_id} modified={self.modified}>"

    @classmethod
    def create(cls, user, idea):
        """Create and return a new vote."""

        return cls(
            user=user, 
            idea=idea, 
            modified=datetime.now())

    @classmethod
    def get_by_idea_id(cls, idea_id):
        return cls.query.filter(Vote.idea_id == idea_id).all()

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter(Vote.user_id == user_id).all()

    @classmethod
    def get_by_user_id_and_idea_id(cls, user_id, idea_id):
        return cls.query.filter(Vote.user_id == user_id, Vote.idea_id == idea_id).first()


    

class Comment(db.Model):
    """A comment."""

    __tablename__ = "comments"

    comment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    modified = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    idea_id = db.Column(db.Integer, db.ForeignKey("ideas.idea_id"))

    user = db.relationship("User", backref="comments")
    idea = db.relationship("Idea", backref="comments")


    def __repr__(self):
        return f"<Comment comment_id={self.idea_id} description={self.description}>"

    @classmethod
    def create(cls, user, idea, description, modified=None):
        """Create and return a new comment."""
        if not modified:
            modified = datetime.now()

        return cls(
            user=user,
            idea=idea,
            description=description,
            modified=modified
            )

    @classmethod
    def update(cls, comment_id, new_description):
        """ Update a idea given idea_id and the updated title and description. """
        comment = cls.query.get(comment_id)
        comment.description = new_description
        comment.modified = datetime.now()

    @classmethod
    def get_by_id(cls, comment_id):
        """Return a comment by primary key."""

        return cls.query.get(comment_id)

    @classmethod
    def get_by_idea_id(cls, idea_id):
        return cls.query.filter(Comment.idea_id == idea_id).all()

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter(Comment.user_id == user_id).all()



def connect_to_db(flask_app, db_uri="postgresql:///ideas", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app)