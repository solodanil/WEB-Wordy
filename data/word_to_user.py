import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Vocabulary(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'vocabulary'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    word_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('word.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), index=True)
    lvl = sqlalchemy.Column(sqlalchemy.Integer, default=1)

    user = orm.relation('User')
    word = orm.relation('Word')

    def __repr__(self):
        return f'<word_to_user id{self.id} {self.word} {self.user} lvl{self.lvl}>'
