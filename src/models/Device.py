from src.database import db


class Device(db.Model):
    __tablename__ = 'Device'

    DeviceID = db.Column(db.Integer, primary_key=True)
    DeviceToken = db.Column(db.VARCHAR, nullable=False, unique=True)
    DeviceType = db.Column(db.VARCHAR, nullable=False)
    OwnerID = db.Column(db.Integer, db.ForeignKey('User.UserID'), nullable=False)
    BatteryPercent = db.Column(db.Integer, default=0)
    Latitude = db.Column(db.REAL, default=0.0)
    Longitude = db.Column(db.REAL, default=0.0)

    def __init__(self, deviceToken, DeviceType, OwnerID):
        self.DeviceToken = deviceToken
        self.DeviceType = DeviceType
        self.OwnerID = OwnerID

    def create(self):
        db.session.add(self)
        db.session.commit()
