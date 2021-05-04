from flask import url_for
from flask_admin.contrib import sqla
from flask_login import current_user
from werkzeug.utils import redirect


class MainView(sqla.ModelView):
    can_export = True

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth'))


class UserView(MainView):
    column_searchable_list = ['name', 'surname', 'email', 'social_id']
