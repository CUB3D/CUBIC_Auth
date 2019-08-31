from src.database import db
import time


class UserApplication(db.Model):
    __tablename__ = 'UserApplication'

    UserApplicationID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    ApplicationID = db.Column(db.Integer, db.ForeignKey('Application.ApplicationID'), nullable=False)
    Token = db.Column(db.VARCHAR(126), nullable=False, unique=True)

    def __init__(self, userID, applicationID, token):
        self.UserID = userID
        self.ApplicationID = applicationID
        self.Token = token

    def create(self):
        db.session.add(self)
        db.session.commit()
