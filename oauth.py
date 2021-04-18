import json

from flask import current_app, url_for, request
from rauth import OAuth2Service
from werkzeug.utils import redirect


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]


class VKSignIn(OAuthSignIn):
    def __init__(self):
        super(VKSignIn, self).__init__('vk')
        self.service = OAuth2Service(
            name='vk',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://oauth.vk.com/authorize',
            access_token_url='https://oauth.vk.com/access_token',
            base_url='https://api.vk.com/method/',
        )

    def authorize(self):
        print(0)
        print(self.service.get_authorize_url(
            scope='friends',
            response_type='code',
            redirect_uri=self.get_callback_url(),
            v='5.130'))
        print(1)
        return redirect(self.service.get_authorize_url(
            scope='friends',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'v': '5.130',
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )
        me = oauth_session.get('me').json()
        print(me)
        # return (
        #     'facebook$' + me['id'],
        #     me.get('email').split('@')[0],  # Facebook does not provide
        #                                     # username, so the email's user
        #                                     # is used instead
        #     me.get('email')
        # )
