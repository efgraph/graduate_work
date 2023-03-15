from authlib.integrations.flask_client import OAuth

from settings import settings

oauth = OAuth()

oauth.register(
    name=settings.oauth.name,
    server_metadata_url=settings.oauth.server_metadata_url,
    client_id=settings.oauth.client_id,
    client_secret=settings.oauth.client_secret,
    client_kwargs={
        'scope': 'openid email profile'
    }
)
