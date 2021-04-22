from flask.json import jsonify
from flask_restful import Resource, abort

from data import db_session
from data.user import User


def abort_if_user_not_found(social_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.social_id == social_id).first()
    if not user:
        abort(404, message=f"User {social_id} not found")


class UserResource(Resource):
    def get(self, social_id):
        abort_if_user_not_found(social_id)
        session = db_session.create_session()
        user = session.query(User).filter(User.social_id == social_id).first()
        print(user)
        return jsonify({'user': user.to_dict(only=('id', 'is_admin', 'name'))})
