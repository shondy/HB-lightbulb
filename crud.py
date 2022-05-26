"""CRUD operations."""

from model import db, User, Idea, Vote, Comment, connect_to_db
from sqlalchemy import func, case, or_


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

def get_user_ideas_with_votes(user_id, page, perpage):
    """Return all ideas made by user with total votes on the page."""
    
    ideas_with_votes = db.session.query(
        Idea.idea_id, 
        Idea.title, 
        func.count(Vote.vote_id).label("total_votes")
        ).outerjoin(Vote).filter(Idea.user_id==user_id).group_by(Idea.idea_id).order_by(Idea.modified.desc()).paginate(page, perpage, error_out = False)


    return ideas_with_votes

def get_voted_by_user_ideas_with_votes(user_id, page, perpage):
    """Return all ideas made by user with total votes on the page."""
    
    ideas_with_votes = db.session.query(
        Idea.idea_id, 
        Idea.title, 
        func.count(Vote.vote_id).label("total_votes"),
        func.count(case(
        [((Vote.user_id == user_id), 1)])).label("user_vote")
        ).join(Vote).filter(Vote.user_id==user_id).group_by(Idea.idea_id).order_by(Idea.modified.desc()).paginate(page, perpage, error_out = False)


    return ideas_with_votes

def get_most_voted_user_idea(user_id):
    """Return most voted and most new user idea."""
    
    idea_with_votes = db.session.query(
        Idea.idea_id, 
        Idea.title, 
        func.count(Vote.vote_id).label("total_votes")
        ).outerjoin(Vote).filter(Idea.user_id==user_id).group_by(Idea.idea_id).order_by(func.count(Vote.vote_id).desc(), Idea.modified.desc()).first()


    return idea_with_votes

def get_ideas_with_votes_for_search(user_id, search, sort, page, perpage):
    """Return all ideas with total votes and votes made by user on the page 
    which title and description contain words from search."""

    ideas_with_votes = Idea.query.msearch(search, fields=['title', 'description']).outerjoin(Vote)
    ideas = Idea.query.msearch(search, fields=['title', 'description']).all()
    print("ideas=================", ideas, len(ideas))

    if user_id is None:
        ideas_with_votes = ideas_with_votes.add_columns(
                    Idea.idea_id, 
                    Idea.title, 
                    func.count(Vote.vote_id).label("total_votes")
                    )
    else:
        ideas_with_votes = ideas_with_votes.add_columns(
                    Idea.idea_id, 
                    Idea.title, 
                    func.count(Vote.vote_id).label("total_votes"),
                    func.count(case(
                    [((Vote.user_id == user_id), 1)])).label("user_vote")
                    )

    ideas_with_votes = ideas_with_votes.group_by(Idea.idea_id)

    # print("ideas_with_votes=========", ideas_with_votes.all())

    if sort == "latest":
        ideas_with_votes = ideas_with_votes.order_by(Idea.modified.desc())
    elif sort == "votes":
        ideas_with_votes = ideas_with_votes.order_by(
            func.count(Vote.vote_id).desc(), 
            Idea.modified.desc()
            )

    return ideas_with_votes.paginate(page, perpage, error_out = False)
    


if __name__ == "__main__":
    from server import app

    connect_to_db(app)
