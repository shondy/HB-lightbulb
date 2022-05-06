"""CRUD operations."""

from model import db, User, Idea, Vote, Comment, connect_to_db
from sqlalchemy import func, case

def get_ideas_with_votes(user_id, page, per_page):
    """Return all ideas with total votes and votes made by user on the page."""
    if user_id is None:
        ideas_with_votes = db.session.query(
            Idea.idea_id, 
            Idea.title, 
            func.count(Vote.vote_id).label("total_votes")
            ).outerjoin(Vote).group_by(Idea.idea_id).order_by(Idea.idea_id).paginate(page, per_page, error_out = False)


    else:
        ideas_with_votes = db.session.query(
            Idea.idea_id, 
            Idea.title, 
            func.count(Vote.vote_id).label("total_votes"),
            func.count(case(
            [((Vote.user_id == user_id), 1)])).label("user_vote")
            ).outerjoin(Vote).group_by(Idea.idea_id).order_by(Idea.idea_id).paginate(page, per_page, error_out = False)


    return ideas_with_votes

if __name__ == "__main__":
    from server import app

    connect_to_db(app)
