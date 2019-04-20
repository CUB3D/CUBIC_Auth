# -*- coding: utf-8 -*-

from flask_alembic import Alembic
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy



# Database

db = SQLAlchemy()


def init(app):
    db.init_app(app)
