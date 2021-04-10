import datetime
import sqlalchemy

from .db_session import SqlAlchemyBase

class Users(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # social_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    # phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    # email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    registration_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=datetime.datetime.now())