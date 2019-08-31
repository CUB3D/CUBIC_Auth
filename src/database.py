# -*- coding: utf-8 -*-

# from alembic import Alembic
import alembic
from flask_sqlalchemy import SQLAlchemy
# Database

db = SQLAlchemy()


def init(app):
    db.init_app(app)
