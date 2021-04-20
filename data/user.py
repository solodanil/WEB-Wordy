import datetime
import sqlalchemy
from flask_login import UserMixin
import sqlalchemy.orm as orm

from .db_session import SqlAlchemyBase

club_to_user = sqlalchemy.Table(
    'club_to_user',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('club', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('speaking_club.id')),
    sqlalchemy.Column('user', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id'))
)


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
    words = orm.relation("Vocabulary", back_populates='user')

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.social_id} {self.email}'
