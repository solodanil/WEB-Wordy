import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    social_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, unique=True)
    phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    registration_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    speaking_club = orm.relation("SpeakingClub",
                                 secondary="club_to_user",
                                 backref="user")

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.social_id} {self.email}'
