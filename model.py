"""Models for movie ratings app."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import bcrypt
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


db = SQLAlchemy()

url_ideas ="http://localhost:5000/ideas/"
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "lightbulb.shondy@gmail.com"
password = os.environ['NOTIFICATION_PASSWORD']
context = ssl.create_default_context()


class User(db.Model):
    """A user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    #password = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    # ratings = a list of Rating objects

    def __repr__(self):
        return f"<User user_id={self.user_id} username={self.username} email={self.email}>"

    @classmethod
    def all_users(cls):
        return cls.query.all()

    # using property decorator
    # define a getter function
    @property
    def password(self):
        return self.password_hash

    # a setter function
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(password, bcrypt.gensalt())

    def verify_password(self, password):
        # Check hashed password. Using bcrypt, the salt is saved into the hash itself
        return bcrypt.checkpw(password, self.password_hash)


    @classmethod
    def create(cls, username, email, password):
        """Create and return a new user."""
        if cls.get_by_username(username) is not None:
            raise ValueError(f"Username {username} is already taken. Try again.")
        
        if cls.get_by_email(email) is not None:
            raise ValueError(f"Accont with email {email} already exists. Try again.")

        return cls(email=email, username=username, password=password)
    
    @classmethod
    def update(cls, user_id, username, email, password, confirm_password):
        """Update and return a new user."""
        user = cls.get_by_id(user_id)

        if not user.verify_password(confirm_password):
            raise ValueError("Wrong current password. Try again.")

        # if user.username != username and cls.query.filter_by(username=username).first() is not None:
        if user.username != username and cls.get_by_username(username) is not None:
            raise ValueError(f"Username {username} is already taken. Try again.")
        
        if user.email != email and cls.get_by_email(email) is not None:
            raise ValueError(f"Accont with email {email} already exists. Try again.")

        user.username = username
        user.email = email
        user.password = password

        return user

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



class Idea(db.Model):
    """An idea."""

    __tablename__ = "ideas"

    idea_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200))
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
    def update(cls, idea_id, new_title, new_description, new_link):
        """ Update a idea given idea_id and the updated title and description. """
        idea = cls.get_by_id(idea_id)
        idea.title = new_title
        idea.description = new_description
        idea.link = new_link
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
        return cls.query.filter(cls.idea_id == idea_id).all()

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter(cls.user_id == user_id).all()

    @classmethod
    def get_by_user_id_and_idea_id(cls, user_id, idea_id):
        return cls.query.filter(cls.user_id == user_id, cls.idea_id == idea_id).first()



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
        
        comment = cls(
            user=user,
            idea=idea,
            description=description,
            modified=modified
            )

        comment.email_notification()

        return comment

    @classmethod
    def update(cls, comment_id, new_description):
        """ Update a idea given idea_id and the updated title and description. """
        comment = cls.get_by_id(comment_id)
        comment.description = new_description
        comment.modified = datetime.now()

        comment.email_notification()

    @classmethod
    def get_by_id(cls, comment_id):
        """Return a comment by primary key."""

        return cls.query.get(comment_id)

    @classmethod
    def get_by_idea_id(cls, idea_id):
        return cls.query.filter(cls.idea_id == idea_id).order_by(cls.modified.desc()).all()

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter(cls.user_id == user_id).order_by(cls.modified.desc()).all()

    def email_notification(self):
        # send an email notification to the user whose idea has been commented on
        receiver_email = self.idea.user.email

        message = MIMEMultipart("alternative")

        message["Subject"] = "LightBulb notification"
        message["From"] = sender_email
        message["To"] = receiver_email
        
        text = f"""\
        Hi {self.idea.user.username},

        There is a new/updated comment to your idea {self.idea.title} {url_ideas}{self.idea_id}/comments:
        {self.description}"""

        html = f"""\
        <html>
        <body>
            <p>
                Hi {self.idea.user.username},
            </p>
            <p>
                There is a new/updated comment to your idea <a href="{url_ideas}{self.idea_id}/comments">{self.idea.title}</a> :
            </p>
            <p>
                {self.description}
            </p>
        </body>
        </html>
        """

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message, which is the MIMEMultipart("alternative") instance
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())


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