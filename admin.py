from flask import url_for
from flask_admin.contrib import sqla
from flask_admin.contrib.fileadmin import FileAdmin
from flask_login import current_user
from werkzeug.utils import redirect

from data import db_session
from data.user import User


class MainView(sqla.ModelView):
    can_export = True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect('/auth')


class FileView(FileAdmin):
    def is_accessible(self):
        if not current_user.is_anonymous:
            db_sess = db_session.create_session()
            return db_sess.query(User).get(current_user.id).access_level.static_files


class UserView(MainView):
    column_searchable_list = ['name', 'surname', 'email', 'social_id']
    column_filters = ['access_level', 'speaking_club']
    can_export = True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect('/auth')

    def is_accessible(self):
        if not current_user.is_anonymous:
            db_sess = db_session.create_session()
            return db_sess.query(User).get(current_user.id).access_level.admin_panel_users


class ClubView(MainView):
    column_searchable_list = ['title']

    def is_accessible(self):
        if not current_user.is_anonymous:
            db_sess = db_session.create_session()
            return db_sess.query(User).get(current_user.id).access_level.admin_panel_clubs


class CollectionView(MainView):
    column_searchable_list = ['name']
    can_export = True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect('/auth')

    def is_accessible(self):
        if not current_user.is_anonymous:
            db_sess = db_session.create_session()
            return db_sess.query(User).get(current_user.id).access_level.admin_panel_collections


class VocabularyView(MainView):
    can_export = True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect('/auth')

    def is_accessible(self):
        if not current_user.is_anonymous:
            db_sess = db_session.create_session()
            return db_sess.query(User).get(current_user.id).access_level.admin_panel_vocabulary


class AccessLevelView(MainView):
    can_export = True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect('/auth')

    def is_accessible(self):
        if not current_user.is_anonymous:
            db_sess = db_session.create_session()
            return db_sess.query(User).get(current_user.id).access_level.admin_panel_access
