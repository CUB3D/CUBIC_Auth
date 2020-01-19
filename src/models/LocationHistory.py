from src.database import db
import time


class LocationHistory(db.Model):
    __tablename__ = 'LocationHistory'

    ID = db.Column(db.Integer, primary_key=True)
    DeviceID = db.Column(db.Integer, db.ForeignKey('Device.DeviceID'), nullable=False)
    Latitude = db.Column(db.REAL, nullable=False, default=0.0)
    Longitude = db.Column(db.REAL, nullable=False, default=0.0)
    CreationTime = db.Column(db.Integer, nullable=False)

    def __init__(self, deviceID, lat, long, time=int(time.time())):
        self.DeviceID = deviceID
        self.Latitude = lat
        self.Longitude = long
        self.CreationTime = time

    def create(self):
        db.session.add(self)
        db.session.commit()
