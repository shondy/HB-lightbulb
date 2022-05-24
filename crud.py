"""CRUD operations."""

from model import db, User, Idea, Vote, Comment, connect_to_db
from sqlalchemy import func, case, or_

def get_ideas_with_votes(user_id, page, per_page):
    """Return all ideas with total votes and votes made by user on the page."""
    if user_id is None:
        ideas_with_votes = db.session.query(
            Idea.idea_id, 
            Idea.title, 
            func.count(Vote.vote_id).label("total_votes")
            ).outerjoin(Vote).group_by(Idea.idea_id).order_by(Idea.idea_id.desc()).paginate(page, per_page, error_out = False)


    else:
        ideas_with_votes = db.session.query(
            Idea.idea_id, 
            Idea.title, 
            func.count(Vote.vote_id).label("total_votes"),
            func.count(case(
            [((Vote.user_id == user_id), 1)])).label("user_vote")
            ).outerjoin(Vote).group_by(Idea.idea_id).order_by(Idea.idea_id.desc()).paginate(page, per_page, error_out = False)


    return ideas_with_votes


def get_idea_votes(user_id, idea_id):
    """Return all ideas with total votes and votes made by user on the page."""
    if user_id is None:
        idea_votes = db.session.query(
            Idea.idea_id, 
            func.count(Vote.vote_id).label("total_votes")
            ).outerjoin(Vote).filter(Idea.idea_id==idea_id).group_by(Idea.idea_id).first()


    else:
        idea_votes = db.session.query(
            Idea.idea_id, 
            Idea.title, 
            func.count(Vote.vote_id).label("total_votes"),
            func.count(case(
            [((Vote.user_id == user_id), 1)])).label("user_vote")
            ).outerjoin(Vote).filter(Idea.idea_id==idea_id).group_by(Idea.idea_id).first()

    return idea_votes

def get_user_ideas_with_votes(user_id, page, per_page):
    """Return all ideas made by user with total votes on the page."""
    
    ideas_with_votes = db.session.query(
        Idea.idea_id, 
        Idea.title, 
        func.count(Vote.vote_id).label("total_votes")
        ).outerjoin(Vote).filter(Idea.user_id==user_id).group_by(Idea.idea_id).order_by(Idea.modified.desc()).paginate(page, per_page, error_out = False)


    return ideas_with_votes

def get_voted_by_user_ideas_with_votes(user_id, page, per_page):
    """Return all ideas made by user with total votes on the page."""
    
    ideas_with_votes = db.session.query(
        Idea.idea_id, 
        Idea.title, 
        func.count(Vote.vote_id).label("total_votes"),
        func.count(case(
        [((Vote.user_id == user_id), 1)])).label("user_vote")
        ).join(Vote).filter(Vote.user_id==user_id).group_by(Idea.idea_id).order_by(Idea.modified.desc()).paginate(page, per_page, error_out = False)


    return ideas_with_votes

def get_most_voted_user_idea(user_id):
    """Return most voted and most new user idea."""
    
    idea_with_votes = db.session.query(
        Idea.idea_id, 
        Idea.title, 
        func.count(Vote.vote_id).label("total_votes")
        ).outerjoin(Vote).filter(Idea.user_id==user_id).group_by(Idea.idea_id).order_by(func.count(Vote.vote_id).desc(), Idea.modified.desc()).first()


    return idea_with_votes

def get_ideas_with_votes_for_search(user_id, search, sort, page, per_page):
    """Return all ideas with total votes and votes made by user on the page 
    which title and description contain words from search."""

    words = search.split()
    search = "%".join(words)
    search = "%" + search + "%"
    print("search======================", search)

    if sort == "latest":
        if user_id is None:
            ideas_with_votes = db.session.query(
                Idea.idea_id, 
                Idea.title, 
                func.count(Vote.vote_id).label("total_votes")
                ).outerjoin(Vote).filter(or_(Idea.title.like(search), Idea.description.like(search))
                ).group_by(Idea.idea_id).order_by(Idea.modified.desc()).paginate(page, per_page, error_out = False)


        else:
            ideas_with_votes = db.session.query(
                Idea.idea_id, 
                Idea.title, 
                func.count(Vote.vote_id).label("total_votes"),
                func.count(case(
                [((Vote.user_id == user_id), 1)])).label("user_vote")
                ).outerjoin(Vote).filter(or_(Idea.title.like(search), Idea.description.like(search))
                ).group_by(Idea.idea_id).order_by(Idea.modified.desc()).paginate(page, per_page, error_out = False)

    else: # sort == "votes":
        if user_id is None:
            ideas_with_votes = db.session.query(
                Idea.idea_id, 
                Idea.title, 
                func.count(Vote.vote_id).label("total_votes")
                ).outerjoin(Vote).filter(or_(Idea.title.like(search), Idea.description.like(search))
                ).group_by(Idea.idea_id).order_by(func.count(Vote.vote_id).desc(), Idea.modified.desc()).paginate(page, per_page, error_out = False)


        else:
            ideas_with_votes = db.session.query(
                Idea.idea_id, 
                Idea.title, 
                func.count(Vote.vote_id).label("total_votes"),
                func.count(case(
                [((Vote.user_id == user_id), 1)])).label("user_vote")
                ).outerjoin(Vote).filter(or_(Idea.title.like(search), Idea.description.like(search))
                ).group_by(Idea.idea_id).order_by(func.count(Vote.vote_id).desc(), Idea.modified.desc()).paginate(page, per_page, error_out = False)

    return ideas_with_votes



if __name__ == "__main__":
    from server import app

    connect_to_db(app)
