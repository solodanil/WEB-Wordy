import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

word_to_collection = sqlalchemy.Table(
    'word_to_collection',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('collection', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('collection.id')),
    sqlalchemy.Column('word', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('word.id'))
)

collection_to_club = sqlalchemy.Table(
    'collection_to_club',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('speaking_club', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('speaking_club.id')),
    sqlalchemy.Column('collection', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('collection.id'))
)


class Collection(SqlAlchemyBase):
    __tablename__ = 'collection'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    word = orm.relation("Word",
                        secondary="word_to_collection",
                        backref="collection")

    def __repr__(self):
        return f'<Collection {self.id} {self.name}>'


class Word(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'word'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    word = sqlalchemy.Column(sqlalchemy.String, index=True)

    def __repr__(self):
        return f'<Word {self.id} {self.word}>'
