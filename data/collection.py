import datetime
import sqlalchemy

from .db_session import SqlAlchemyBase

class Collection(SqlAlchemyBase):
    __tablename__ = 'сollection'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)