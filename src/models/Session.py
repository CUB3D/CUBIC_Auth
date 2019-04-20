from src.database import db


class Session(db.Model):
    __tablename__ = 'Session'

    SessionID = db.Column(db.Integer, primary_key=True)
    SessionToken = db.Column(db.VARCHAR, nullable=False, unique=True)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=True) #,

    def __init__(self, token, userID):
        self.SessionToken = token
        self.UserID = userID

    def create(self):
        db.session.add(self)
        db.session.commit()
