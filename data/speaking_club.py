import datetime
import sqlalchemy
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


class SpeakingClub(SqlAlchemyBase):
    __tablename__ = 'speaking_club'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.Time, default=datetime.time, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.Date, default=datetime.date.today(), nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    number_of_seats = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # author = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    collection = orm.relation("Collection",
                              secondary="collection_to_club",
                              backref="speaking_club")

    def __repr__(self):
        return f'<speaking club> {self.id} {self.title}'
