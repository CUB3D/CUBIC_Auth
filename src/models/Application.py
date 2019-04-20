from src.database import db
import time


class Application(db.Model):
    __tablename__ = 'Application'

    ApplicationID = db.Column(db.Integer, primary_key=True)
    ApplicationToken = db.Column(db.VARCHAR, nullable=False, unique=True)
    CreationTime = db.Column(db.Integer, nullable=False)
    OwnerID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    Description = db.Column(db.VARCHAR, nullable=False)
    ApplicationName = db.Column(db.VARCHAR, nullable=False)
    url = db.Column(db.VARCHAR, nullable=False)

    def __init__(self, token, ownerID, description, applicationName, url, time=int(time.time())):
        self.ApplicationToken = token
        self.OwnerID = ownerID
        self.Description = description
        self.ApplicationName = applicationName
        self.url = url
        self.CreationTime = time

    def create(self):
        db.session.add(self)
        db.session.commit()
