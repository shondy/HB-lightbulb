"""Script to seed database."""

import os
import json
from random import choice, sample
from datetime import datetime

import model
import server

os.system("dropdb ideas")
os.system("createdb ideas")

model.connect_to_db(server.app)
model.db.create_all()

# Create 10 users
users_in_db = []
for n in range(10):
    username = f"test{n}"
    email = f"user{n}@test.com"
    password = f"test{n}"

    db_user = model.User.create(email, username, password)
    users_in_db.append(db_user)

model.db.session.add_all(users_in_db)
# print("users--------------------------->", users_in_db)

# Load ideas data from JSON file
with open("data/ideas.json") as f:
    idea_data = json.loads(f.read())

# Create ideas, store them in list so we can save them in db
ideas_in_db = []
for idea in idea_data:
    title, description, link = (
        idea["title"],
        idea["description"],
        idea["link"],
    )
    modified = datetime.strptime(idea["modified"], "%Y-%m-%d")
    user = choice(users_in_db)

    db_idea = model.Idea.create(user, title, description, link, modified)
    ideas_in_db.append(db_idea)

model.db.session.add_all(ideas_in_db)

# each of 10 created users will make 3 votes and 3 comments
for user in users_in_db:
    random_ideas = sample(ideas_in_db, 3)
    votes = [model.Vote.create(user, idea) for idea in random_ideas]
    model.db.session.add_all(votes)

    for _ in range(3):
        random_idea = choice(ideas_in_db)
        random_comment = choice(["cool idea", "great idea", "not usefull", "would like to have this app", "would like to implement", "please explain in detail"])

        comment = model.Comment.create(user, random_idea, random_comment)
        model.db.session.add(comment)


model.db.session.commit()