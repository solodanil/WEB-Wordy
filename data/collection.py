import datetime
import sqlalchemy

from .db_session import SqlAlchemyBase

word_to_collection = sqlalchemy.Table(
    'word_to_collection',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('collection', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('collection.id')),
    sqlalchemy.Column('word', sqlalchemy.String)
)


class Collection(SqlAlchemyBase):
    __tablename__ = 'collection'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
