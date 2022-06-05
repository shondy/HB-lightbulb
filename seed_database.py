"""Script to seed database."""

import os
import json
from random import choice, sample
from datetime import datetime, timedelta
# import sys

import model
import server

# dbname = sys.argv[1]
# os.system(f"dropdb {dbname}")
os.system("dropdb ideas")
os.system("createdb ideas")

model.connect_to_db(server.app)
model.db.create_all()
# model.search.create_index()

# Create 5 users
users_in_db = []
for n in range(6):
    username = f"test{n}"
    email = f"user{n}@test.com"
    description = f"I'm a test user {n}. Happy to be useful."
    password = f"test{n}A!!"
    description = f"I'm test user{n}. Happy to help."
    created = datetime.today() - timedelta(days=n)

    db_user = model.User(username=username, email=email, password=password, description=description, email_confirmed=True, created=created)
    users_in_db.append(db_user)

model.db.session.add_all(users_in_db)
# print("users--------------------------->", users_in_db)

# Load ideas data from JSON file
with open("data/ideas.json") as f:
    idea_data = json.loads(f.read())

# Create ideas, store them in list so we can save them in db
ideas_in_db = []
for idea in idea_data:
    title, description, link, image = (
        idea["title"],
        idea["description"],
        idea["link"],
        idea["image"]
    )

    modified = datetime.strptime(idea["modified"], "%Y-%m-%d")

    user = choice(users_in_db)
    

    db_idea = model.Idea(user=user, title=title, description=description, link=link, image=image, modified=modified)
    ideas_in_db.append(db_idea)

model.db.session.add_all(ideas_in_db)

# each of 6 created users will make 5 votes and 5 comments
for user in users_in_db:
    random_ideas = sample(ideas_in_db, 5)
    votes = [model.Vote(user=user, idea=idea) for idea in random_ideas]
    model.db.session.add_all(votes)

    for _ in range(5):
        random_idea = choice(ideas_in_db)
        random_comment = choice([
            "Was certainty remaining engrossed applauded sir how discovery. Settled opinion how enjoyed greater joy adapted too shy. Now properly surprise expenses interest nor replying she she. Bore tall nay many many time yet less. Doubtful for answered one fat indulged margaret sir shutters together. Ladies so in wholly around whence in at. Warmth he up giving oppose if. Impossible is dissimilar entreaties oh on terminated. Earnest studied article country ten respect showing had. But required offering him elegance son improved informed",
            "Unpacked now declared put you confined daughter improved. Celebrated imprudence few interested especially reasonable off one. Wonder bed elinor family secure met. It want gave west into high no in. Depend repair met before man admire see and. An he observe be it covered delight hastily message. Margaret no ladyship endeavor ye to settling",
            "Building mr concerns servants in he outlived am breeding. He so lain good miss when sell some at if. Told hand so an rich gave next. How doubt yet again see son smart. While mirth large of on front. Ye he greater related adapted proceed entered an. Through it examine express promise no. Past add size game cold girl off how old",
            "Looking started he up perhaps against. How remainder all additions get elsewhere resources. One missed shy wishes supply design answer formed. Prevent on present hastily passage an subject in be. Be happiness arranging so newspaper defective affection ye. Families blessing he in to no daughter",
            "Now for manners use has company believe parlors. Least nor party who wrote while did. Excuse formed as is agreed admire so on result parish. Put use set uncommonly announcing and travelling. Allowance sweetness direction to as necessary. Principle oh explained excellent do my suspected conveying in. Excellent you did therefore perfectly supposing described",
            "At ourselves direction believing do he departure. Celebrated her had sentiments understood are projection set. Possession ye no mr unaffected remarkably at. Wrote house in never fruit up. Pasture imagine my garrets an he. However distant she request behaved see nothing. Talking settled at pleased an of me brother weather",
            "Bringing unlocked me an striking ye perceive. Mr by wound hours oh happy. Me in resolution pianoforte continuing we. Most my no spot felt by no. He he in forfeited furniture sweetness he arranging. Me tedious so to behaved written account ferrars moments. Too objection for elsewhere her preferred allowance her. Marianne shutters mr steepest to me. Up mr ignorant produced distance although is sociable blessing. Ham whom call all lain like",
            "Ought these are balls place mrs their times add she. Taken no great widow spoke of it small. Genius use except son esteem merely her limits. Sons park by do make on. It do oh cottage offered cottage in written. Especially of dissimilar up attachment themselves by interested boisterous. Linen mrs seems men table. Jennings dashwood to quitting marriage bachelor in. On as conviction in of appearance apartments boisterous",
            "Of be talent me answer do relied. Mistress in on so laughing throwing endeavor occasion welcomed. Gravity sir brandon calling can. No years do widow house delay stand. Prospect six kindness use steepest new ask. High gone kind calm call as ever is. Introduced melancholy estimating motionless on up as do. Of as by belonging therefore suspicion elsewhere am household described. Domestic suitable bachelor for landlord fat",
            "Stronger unpacked felicity to of mistaken. Fanny at wrong table ye in. Be on easily cannot innate in lasted months on. Differed and and felicity steepest mrs age outweigh. Opinions learning likewise daughter now age outweigh. Raptures stanhill my greatest mistaken or exercise he on although. Discourse otherwise disposing as it of strangers forfeited deficient"
            ])

        comment = model.Comment(user=user, idea=random_idea, description=random_comment, modified=datetime.strptime(idea["modified"], "%Y-%m-%d"))
        model.db.session.add(comment)


model.db.session.commit()