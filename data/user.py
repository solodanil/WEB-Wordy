import datetime
import sqlalchemy
from flask_login import UserMixin
import sqlalchemy.orm as orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

club_to_user = sqlalchemy.Table(
    'club_to_user',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('club', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('speaking_club.id')),
    sqlalchemy.Column('user', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id'))
)


class AccessLevel(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'access_level'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    index = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    club_booking = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    words_learning = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    new_club = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    new_collection = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    admin_panel_users = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel_users_create = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel_users_edit = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    admin_panel_clubs = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel_clubs_create = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel_clubs_edit = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    admin_panel_collections = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel_collections_create = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel_collections_edit = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    admin_panel_vocabulary = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel_vocabulary_create = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel_vocabulary_edit = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    admin_panel_access = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel_access_create = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    admin_panel_access_edit = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    static_files = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    users = orm.relation('User', back_populates='access_level')

    def __repr__(self):
        return f'{self.name} ({self.id})'


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    social_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, unique=True)
    phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    registration_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    access_level_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("access_level.id"))
    access_level = orm.relation('AccessLevel')
    words = orm.relation("Vocabulary", back_populates='user')

    def __repr__(self):
        return f'<User {self.id} {self.name} {self.social_id} {self.email}>'
