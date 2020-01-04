from src.database import db
import time


class SessionAccess(db.Model):
    __tablename__ = 'SessionAccess'

    UsageID = db.Column(db.Integer, primary_key=True)
    SessionID = db.Column(db.Integer, db.ForeignKey('Session.SessionID'), nullable=False)
    AccessTime = db.Column(db.Integer, nullable=False)
    Success = db.Column(db.Integer, nullable=False)

    def __init__(self, sessionID, success, time=int(time.time())):
        self.SessionID = sessionID
        self.AccessTime = time
        self.Success = success

    def create(self):
        db.session.add(self)
        db.session.commit()
