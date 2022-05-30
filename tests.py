from unittest import TestCase
from server import app
from model import connect_to_db, db, User, Idea, Comment, Vote
from flask import url_for, request, session
from datetime import datetime
import json
import os


class FlaskTestsBasic(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""
        os.system("dropdb idea_testdb")
        os.system("createdb idea_testdb")

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///idea_testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.remove()
        # breakpoint()
        db.drop_all()
        db.engine.dispose()

    def test_index(self):
        """Test homepage page."""

        result = self.client.get("/")
        self.assertIn(b"Lightbulb is a free", result.data)

    def test_login(self):
        """Test login page."""

        result = self.client.post("/login",
                                  headers={'Content-Type': 'application/json'},
                                  json={"email": "user0@test.com", "password": "test0A!!"}
                                  )
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)

    def test_logout(self):
        """Test logout route."""

        with self.client as c:
            with c.session_transaction() as session:
                session['user_id'] = '1'

            result = self.client.get('/logout', follow_redirects=True)

            self.assertNotIn(b'user_id', session)
            self.assertEqual(result.request.path, '/')
            self.assertIn(b'Sign in', result.data)
        
        
    def test_login_failure(self):
        """Test login page with wrong email."""

        result = self.client.post("/login",
                                  headers={'Content-Type': 'application/json'},
                                  json={"email": "user01@test.com", "password": "test0A!!"}
                                  )
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The email or password you entered was incorrect.')
        

class FlaskTestsDatabase(TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///idea_testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    def test_ideas_list_latest_sort(self):
        """Test ideas sorting by last modification."""

        ideas = Idea.query.order_by(Idea.modified.desc()).all()
        result = self.client.get("/all-ideas")

        idx = []

        for i, idea in enumerate(ideas):
            idx.append(result.data.find(idea.title.encode('ascii')))
        
        for i in range(1, len(idx)):
            self.assertLess(idx[i-1], idx[i], f"Strings {ideas[i-1].title} and {ideas[i].title} are in the wrong order")

    def test_ideas_list_voted_sort(self):
        """Test ideas sorting by number of votes."""

        result = self.client.get("/all-ideas?search=&sort=votes&perpage=2&page=2")

        idea1 = Idea.query.get(10)
        idea2 = Idea.query.get(5)

        idx1 = result.data.find(idea1.title.encode('ascii'))
        idx2 = result.data.find(idea2.title.encode('ascii'))
        
        self.assertGreater(idx1, -1, f"Strings {idea1.title} should be on the page")
        self.assertGreater(idx2, -1, f"Strings {idea2.title} should be on the page")
        self.assertLess(idx1, idx2, f"Strings {idea1.title} and {idea2.title} are in the wrong order")

    def test_ideas_list_search(self):
        """Test ideas searching."""

        result = self.client.get("/all-ideas?search=information+time&sort=relevance&perpage=10&page=1")
        
        idea1 = Idea.query.get(3)
        idea2 = Idea.query.get(10)

        idx1 = result.data.find(idea1.title.encode('ascii'))
        idx2 = result.data.find(idea2.title.encode('ascii'))
        num_ideas = result.data.count(b'<a href="/ideas/')
        
        self.assertGreater(idx1, -1, f"Strings {idea1.title} should be on the page")
        self.assertGreater(idx2, -1, f"Strings {idea2.title} should be on the page")
        self.assertLess(idx1, idx2, f"Strings {idea1.title} and {idea2.title} are in the wrong order")
        self.assertEqual(num_ideas, 2, "Wrong amount of ideas")

    def test_idea_comments(self):
        """Test idea comments."""

        result = self.client.get("/ideas/10/comments")
        
        self.assertIn(b'would like to have this app', result.data)


class FlaskTestsLoggedIn(TestCase):
    """Flask tests with user logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()

        # Connect to test database
        connect_to_db(app, "postgresql:///idea_testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as session:
                session['user_id'] = 1

    def tearDown(self):
        """Do at end of every test."""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    def test_create_idea(self):
        """Test creating an idea."""


        result = self.client.post("/ideas",
                                  headers={'Content-Type': 'application/json'},
                                  json={"title": "Lightbulb",
                                  "description": "A collaboration application for sharing and discussing project ideas",
                                  "link": "https://github.com/shondy/HB-lightbulb",}
                                  )
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        idea_id = data["added"]

        idea = Idea.query.get(idea_id)

        self.assertEqual(idea.title, "Lightbulb")
        self.assertEqual(idea.description, "A collaboration application for sharing and discussing project ideas")
        self.assertEqual(idea.link, "https://github.com/shondy/HB-lightbulb")

    def test_update_idea(self):
        """Test updating an idea."""


        result = self.client.put("/ideas/1",
                                  headers={'Content-Type': 'application/json'},
                                  json={"title": "Test",
                                  "description": "Test",
                                  "link": "https://github.com/test/test",}
                                  )
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        idea_id = data["updated"]

        idea = Idea.query.get(idea_id)

        self.assertEqual(idea.title, "Test")
        self.assertEqual(idea.description, "Test")
        self.assertEqual(idea.link, "https://github.com/test/test")

    def test_create_comment(self):
        """Test creating a comment."""


        result = self.client.post("/comments/1",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "description": "Would be a very useful app for HB students",
                                  }
                                  )
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        comment_id = data["added"]

        comment = Comment.query.get(comment_id)

        self.assertEqual(comment.description, "Would be a very useful app for HB students")

    def test_update_comment(self):
        """Test updating a comment."""


        result = self.client.put("/comments/7/1",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "description": "Test",
                                  }
                                  )
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        comment_id = data["updated"]

        comment = Comment.query.get(comment_id)

        self.assertEqual(comment.description, "Test")

    def test_delete_comment(self):
        """Test deleting a comment."""


        result = self.client.delete("/comments/7/1",
                                  headers={'Content-Type': 'application/json'},
                                  )
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        comment_id = data["deleted"]
        self.assertEqual(Comment.query.get(comment_id), None)


    def test_vote(self):
        """Test voting for an idea."""


        result = self.client.post("/votes",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "idea_id": "5",
                                  }
                                  )
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        vote_id = data["added"]

        vote = Vote.query.get(vote_id)

        self.assertEqual(vote.idea_id, 5)

    def test_unvote(self):
        """Test unvoting for an idea."""


        result = self.client.delete("/votes",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "idea_id": "9",
                                  }
                                  )
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        vote_id = data["deleted"]

        self.assertEqual(Vote.query.get(vote_id), None)

    def test_update_user_details(self):
        """Test updating user details."""

        result = self.client.put("/users/1/details",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "username": "superuser",
                                      "description": "I'm the main user in tests"
                                  }
                                  )
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)
        user_id = data["updated"]

        user = User.query.get(user_id)

        self.assertEqual(user.username, "superuser")
        self.assertEqual(user.description, "I'm the main user in tests")

    def test_update_user_password(self):
        """Test updating user password."""

        result = self.client.put("/users/1/password",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "password": "test0A!!9",
                                      "confirm_password": "test0A!!"
                                  }
                                  )
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)

class FlaskTestsLoggedOut(TestCase):
    """Flask tests with user logged out from session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()

        # Connect to test database
        connect_to_db(app, "postgresql:///idea_testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()


    def tearDown(self):
        """Do at end of every test."""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    def test_create_idea_failure(self):
        """Test failure of creating an idea for logged out user."""


        result = self.client.post("/ideas",
                                  headers={'Content-Type': 'application/json'},
                                  json={"title": "Lightbulb",
                                  "description": "A collaboration application for sharing and discussing project ideas",
                                  "link": "https://github.com/shondy/HB-lightbulb",}
                                  )
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User did not login to the application.')

    def test_update_idea_failure(self):
        """Test failure of updating an idea for logged out user."""


        result = self.client.put("/ideas/1",
                                  headers={'Content-Type': 'application/json'},
                                  json={"title": "Test",
                                  "description": "Test",
                                  "link": "https://github.com/test/test",}
                                  )
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User did not login to the application.')


    def test_create_comment_failure(self):
        """Test failure of creating a comment for logged out user."""


        result = self.client.post("/comments/1",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "description": "Would be a very useful app for HB students",
                                  }
                                  )
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User did not login to the application.')

    def test_update_comment_failure(self):
        """Test failure of updating a comment for logged out user."""


        result = self.client.put("/comments/7/1",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "description": "Test",
                                  }
                                  )
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User did not login to the application.')

    def test_delete_comment_failure(self):
        """Test failure of deleting a comment for logged out user."""


        result = self.client.delete("/comments/7/1",
                                  headers={'Content-Type': 'application/json'},
                                  )
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User did not login to the application.')


    def test_vote_failure(self):
        """Test failure of voting for an idea for logged out user."""


        result = self.client.post("/votes",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "idea_id": "5",
                                  }
                                  )
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User did not login to the application.')

    def test_update_user_details_failure(self):
        """Test updating user details."""

        result = self.client.put("/users/1/details",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "username": "superuser",
                                      "description": "I'm the main user in tests"
                                  }
                                  )
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User did not login to the application.')

    def test_update_user_password_failure(self):
        """Test updating user password."""

        result = self.client.put("/users/1/password",
                                  headers={'Content-Type': 'application/json'},
                                  json={
                                      "password": "test0A!!",
                                      "confirm_password": "test0A!!9"
                                  }
                                  )
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'User did not login to the application.')


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
        description = f"I'm test user{n}. Happy to help."
        db_user = User(username=username, email=email, password=password, description=description, email_confirmed=True)
        users_in_db.append(db_user)

    db.session.add_all(users_in_db)

    # Load ideas data from JSON file
    with open("data/ideas.json") as f:
        idea_data = json.loads(f.read())

    # Create ideas, store them in list so we can save them in db
    ideas_in_db = []
    user = users_in_db[0]
    for idx, idea in enumerate(idea_data):
        if idx > 9:
            break

        title, description, link = (
            idea["title"],
            idea["description"],
            idea["link"],
        )
        modified = datetime.strptime(idea["modified"], "%Y-%m-%d")

        if idx > 5:
            user = users_in_db[1]

        db_idea = Idea(user=user, title=title, description=description, link=link, modified=modified)
        ideas_in_db.append(db_idea)

    db.session.add_all(ideas_in_db)

    # Create votes 
    votes_1 = [Vote(user=users_in_db[0], idea=idea) for idea in ideas_in_db[8:]]
    db.session.add_all(votes_1)
    votes_2 = [Vote(user=users_in_db[1], idea=idea) for idea in ideas_in_db[:5]]
    db.session.add_all(votes_2)
    votes_3 = [Vote(user=users_in_db[2], idea=idea) for idea in ideas_in_db[::3]]
    db.session.add_all(votes_3)

    # Create comments
    comment_descr = ["cool idea", "great idea", "not usefull", "would like to have this app", "would like to implement", "please explain in detail"]
    comments_1 = [Comment(user=users_in_db[0], idea=ideas_in_db[i], description=comment_descr[i - 12], modified=datetime.strptime(idea["modified"], "%Y-%m-%d")) for i in range(6, 10)]
    db.session.add_all(comments_1)
    comments_2 = [Comment(user=users_in_db[1], idea=ideas_in_db[i], description=comment_descr[i], modified=datetime.strptime(idea["modified"], "%Y-%m-%d")) for i in range(3)]
    db.session.add_all(comments_2)
    comments_3 = [Comment(user=users_in_db[2], idea=ideas_in_db[3*i], description=comment_descr[i], modified=datetime.strptime(idea["modified"], "%Y-%m-%d")) for i in range(3)]
    db.session.add_all(comments_3)

    # push all data to db
    db.session.commit()

if __name__ == "__main__":
    import unittest

    unittest.main()
    
