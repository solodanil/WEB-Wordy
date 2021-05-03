from random import choice

from flask.json import jsonify
from flask_restful import Resource, abort, reqparse
from sqlalchemy import func

from data import db_session
from data.collection import Word
from data.user import User
from data.word_to_user import Vocabulary
from dictionary import google_dict, translate, emoji, search_image, search_synonyms

parser = reqparse.RequestParser()
parser.add_argument('word_id', required=True, type=int)


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
        return jsonify({'user': user.to_dict(only=('id', 'is_admin', 'name'))})


class VocabularyResource(Resource):
    def get(self, user_social_id):
        abort_if_user_not_found(user_social_id)
        session = db_session.create_session()
        user_id = session.query(User).filter(User.social_id == user_social_id).first().id
        vocabs = session.query(Vocabulary).filter(Vocabulary.user_id == user_id, Vocabulary.lvl <= 10).all()
        vocab = choice(vocabs)
        print(vocab)
        word = vocab.word.word
        incorrect_words = list(
            map(lambda x: x.word, session.query(Word).filter(word != vocab.word).order_by(func.random()).all()[:2]))
        dict_response = google_dict(word)
        return jsonify({
            'word':
                {'word': word,
                 'translation': translate(word),
                 'emoji': emoji(word),
                 'image': search_image(word),
                 'synonyms': search_synonyms(dict_response),
                 'dictionary': dict_response,
                 'word_id': vocab.word.id
                 },
            'lvl': vocab.lvl,
            'incorrect_words': incorrect_words})

    def post(self, user_social_id):
        print(0)
        abort_if_user_not_found(user_social_id)
        session = db_session.create_session()
        word_id = parser.parse_args()['word_id']
        user_id = session.query(User).filter(User.social_id == user_social_id).first().id
        vocab = session.query(Vocabulary).filter(Vocabulary.user_id == user_id, Vocabulary.lvl <= 10,
                                                 Vocabulary.word_id == word_id).first()
        vocab.lvl = vocab.lvl + 1
        print(0)
        print(vocab)
        session.commit()
        return jsonify({'success': True})
