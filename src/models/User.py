from src.database import db
import uuid


class User(db.Model):
    __tablename__ = 'User'

    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.VARCHAR(50), nullable=False, unique=True)
    PasswordHash = db.Column(db.VARCHAR, nullable=False)
    communication_channel = db.Column(db.VARCHAR, nullable=False)

    def __init__(self, username, passwordHash):
        self.Username = username
        self.PasswordHash = passwordHash
        self.communication_channel = str(uuid.UUID())

    def create(self):
        db.session.add(self)
        db.session.commit()
