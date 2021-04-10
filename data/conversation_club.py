import datetime
import sqlalchemy

from .db_session import SqlAlchemyBase

class ConversationClub(SqlAlchemyBase):
    __tablename__ = 'conversation_club'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.Time, default=datetime.time)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    duration = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.timedelta)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    number_of_seats = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)


