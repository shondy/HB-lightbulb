"""Models for movie ratings app."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import bcrypt
from utils import send_email
from random import randint
import json



db = SQLAlchemy()


class User(db.Model):
    """A user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100))
    description = db.Column(db.Text)
    # google_sign_only = True, if user signed in with Google, but never created a password
    # google_sign_only = False, otherwise 
    google_sign_only = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirm_date = db.Column(db.DateTime)
    


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
        
        # if cls.get_by_email(email) is not None:
        #     raise ValueError(f"Accont with email {email} already exists. Try again.")

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
    def create_google_user(cls, username, email):
        """Create user who joined with google account and return a new user."""

        while cls.get_by_username(username):
            username += str(randint(0, 9))

        return cls(email=email, username=username, password='', google_sign_only=True)
    
    @classmethod
    def update_details(cls, user_id, username, description):
        """Update user deatils and return the user."""

        user = cls.get_by_id(user_id)

        if user.username != username and cls.get_by_username(username) is not None:
            raise ValueError(f"Username {username} is already taken. Try again.")
       
        user.username = username
        user.description = description

        return user

    @classmethod
    def update_password(cls, user_id, password, confirm_password):
        """Update user password and return the user."""

        user = cls.get_by_id(user_id)

        if not user.verify_password(confirm_password):
            raise ValueError("Wrong current password. Try again.")

        user.password = password

        return user

    @classmethod
    def update_google_signed_to_unconfirmed(cls, user_id, username, password):
        """if user initially signed with Google and joined with email&password, 
        update user email_confirmation_sent_on and google_sign_only to False."""

        user = cls.get_by_id(user_id)

        if user.username != username and User.get_by_username(username):
            abort(400, f"Username {username} is already taken. Try again.")

        user.username = username
        user.password = password
        user.google_sign_only = False
        user.email_confirmation_sent_on = datetime.now()

        return user

    @classmethod
    def confirm_email(cls, user_id):
        user = cls.get_by_id(user_id)
        user.email_confirmed = True
        user.email_confirmed_on = datetime.now()


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
        """ send an email notification to the user whose idea has been commented on """
        
        receiver_email = self.idea.user.email
        
        text = f"""\
        Hi {self.idea.user.username},

        There is a new/updated comment to your idea {self.idea.title} {url_ideas}{self.idea_id}/comments:
        {self.description}"""

        html = render_template(
            'user_idea_notification.html', 
            username=self.idea.user.username, 
            idea_url=f"http://localhost:5000/ideas/{self.idea_id}/comments", 
            idea_title=self.idea.title,
            comment_description=self.description)
        
        send_email(text, html, "LightBulb notification", receiver_email)

def example_data():
    """Create some sample data."""

    # In case this is run more than once, empty out existing data
    # meta = db.metadata

    # # sorted_tables returns a list of tables sorted in order of foreign key dependency, 
    # # reversed ensure that children are deleted before parents to avoid foreign key violation.
    # for table in reversed(meta.sorted_tables):
    #     print(f'Clear table {table}')
    #     db.session.execute(table.delete())
    # db.session.commit()

    # Create 3 users, store them in list so we can save them in db
    users_in_db = []
    for n in range(3):
        username = f"test{n}"
        email = f"user{n}@test.com"
        password = f"test{n}A!!"
        db_user = User.create(username, email, password)
        users_in_db.append(db_user)

    db.session.add_all(users_in_db)

    # Load ideas data from JSON file
    with open("data/ideas.json") as f:
        idea_data = json.loads(f.read())

    # Create ideas, store them in list so we can save them in db
    ideas_in_db = []
    user = users_in_db[0]
    for idx, idea in enumerate(idea_data):
        title, description, link = (
            idea["title"],
            idea["description"],
            idea["link"],
        )
        modified = datetime.strptime(idea["modified"], "%Y-%m-%d")

        if idx > 11:
            user = users_in_db[1]

        db_idea = Idea.create(user, title, description, link, modified)
        ideas_in_db.append(db_idea)

    db.session.add_all(ideas_in_db)

    # Create votes 
    votes_1 = [Vote.create(users_in_db[0], idea) for idea in ideas_in_db[15:]]
    db.session.add_all(votes_1)
    votes_2 = [Vote.create(users_in_db[1], idea) for idea in ideas_in_db[:6]]
    db.session.add_all(votes_2)
    votes_3 = [Vote.create(users_in_db[2], idea) for idea in ideas_in_db[::3]]
    db.session.add_all(votes_3)

    # Create comments
    comment_descr = ["cool idea", "great idea", "not usefull", "would like to have this app", "would like to implement", "please explain in detail"]
    comments_1 = [Comment.create(users_in_db[0], ideas_in_db[i], comment_descr[i - 12]) for i in range(12, 18)]
    db.session.add_all(comments_1)
    comments_2 = [Comment.create(users_in_db[1], ideas_in_db[i], comment_descr[i]) for i in range(6)]
    db.session.add_all(comments_2)
    comments_3 = [Comment.create(users_in_db[2], ideas_in_db[3*i + 1], comment_descr[i]) for i in range(6)]
    db.session.add_all(comments_3)

    # push all data to db
    db.session.commit()

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

    # app.config['TESTING'] = True
    # # Connect to test database
    # connect_to_db(app, "postgresql:///idea_testdb")
    # db.create_all()
    # example_data()
