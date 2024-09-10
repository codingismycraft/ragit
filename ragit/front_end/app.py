"""Exposes the Sibyl Main web page."""

import datetime
import functools
import logging
import os
import sys
import uuid

import aiohttp
import aiohttp.web as web
import jinja2
import jwt

import ragit.libs.common as common
import ragit.libs.rag_mgr as rag_mgr
import ragit.libs.user_registry as user_registry

_JINJA_ENV = jinja2.Environment(
    loader=jinja2.PackageLoader(
        'templates',
        'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

_CURR_DIR = os.path.dirname(os.path.realpath(__file__))
_PATH_TO_STATIC = os.path.join(_CURR_DIR, 'static')
_CONFIGURATION = common.Configuration(os.path.join(_CURR_DIR, 'config.yaml'))
_DEFAULT_PORT = 13131

logger = logging.getLogger(_CONFIGURATION.settings["web_service"]["name"])

# Aliases.
UserRegistry = user_registry.UserRegistry


class AuthenticationError(Exception):
    """Authentication Error."""


class Globals:
    """Global variables holder.

    :cvar: RagManager rag_manager: The Rag Manager instance for the rag
    collection which is defined in the configuration file. It is instantiated
    once when the service is starting and remains in memory for the rest of
    the lifespan of the program.

    :cvar: str _secret_key:  The secret key that is used for authentication.
    """
    rag_manager = None
    _secret_key = str(uuid.uuid4())

    @classmethod
    def generate_token(cls, user_name, expiration_minutes=3600):
        """Creates a JSON Web Token (JWT) for the given user.

        :param str user_name: The user's username.
        :param int expiration_minutes: The token expiration in minutes.

        :return: The generated JWT token.
        :rtype: str
        """
        payload = {
            'username': user_name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                minutes=expiration_minutes
            )
        }
        token = jwt.encode(payload, cls._secret_key, algorithm='HS256')
        return token

    @classmethod
    def validate_token(cls, token, user_name):
        """Validates the passed in token.

        :param str token: The token to validate.
        :param str user_name: The user name.
        """
        try:
            payload = jwt.decode(token, cls._secret_key, algorithms=['HS256'])
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as ex:
            raise AuthenticationError(str(ex)) from ex


def _raw_headers_to_dict(raw_headers):
    """Converts raw headers to a dictionary."""
    d = {}
    for k, v in raw_headers:
        try:
            d[k.decode('utf-8')] = v.decode('utf-8')
        except Exception as ex:
            logger.exception(ex)
    return d


def web_handler(handler_func):
    """Wraps a handler function adding standard processing."""

    @functools.wraps(handler_func)
    async def _inner(self, request):
        """The decorator function."""
        try:
            raw_headers = _raw_headers_to_dict(request.raw_headers)
            real_ip = raw_headers.get("X-Real-IP")
            logger.info(f"Connected User IP: {real_ip}")
            return await handler_func(self, request)
        except web.HTTPFound:
            # must be a redirect..
            raise
        except Exception as ex:
            logger.exception(ex)
            raise aiohttp.web.HTTPInternalServerError()

    return _inner


class RagitHandler:
    """Implements all the web handlers used from the service."""

    @web_handler
    async def main_page_handler(self, request):
        """Displays the main page.

        :param request: The web request.
        """
        try:
            auth_token = request.cookies.get('ragit_auth_token')
            user_name = request.cookies.get('user_name')
            Globals.validate_token(auth_token, user_name)
        except AuthenticationError:
            return web.HTTPFound('/login')
        else:
            template = _JINJA_ENV.get_template('index.html')
            collection_name = Globals.rag_manager.get_rag_collection_name()
            txt = template.render(
                host=request.host, collection_name=collection_name
            )
            response = web.Response(
                body=txt.encode(),
                content_type='text/html'
            )
            response.set_cookie('ragit_auth_token', auth_token)
            response.set_cookie('user_name', user_name)
            logger.info("Serving main page.")
            return response

    @web_handler
    async def query_handler(self, request):
        """Handles a query that is submitted by the chatbot user.

        :param request: The web request.
        """
        try:
            auth_token = request.cookies.get('ragit_auth_token')
            user_name = request.cookies.get('user_name')
            Globals.validate_token(auth_token, user_name)
        except AuthenticationError:
            return web.HTTPFound('/login')
        try:
            data = await request.json()
            query = data.get('query')
            t1 = datetime.datetime.now()
            response = Globals.rag_manager.query(query)

            t2 = datetime.datetime.now()

            msg_id = UserRegistry.insert_message(
                user_name, t1, query, response, t2
            )
            return web.json_response(
                {
                    "response": response,
                    "message_id": msg_id
                }
            )
        except Exception as ex:
            return web.json_response({"response": str(ex)})

    @web_handler
    async def default_handler(self, request):
        """Redirects to login."""
        return web.HTTPFound('/login')

    @web_handler
    async def signup_screen(self, request):
        """Displays the signupscreen.

        :param request: The web request.
        """
        template = _JINJA_ENV.get_template('signup.html')
        txt = template.render(host=request.host)
        return web.Response(
            body=txt.encode(),
            content_type='text/html'
        )

    @web_handler
    async def vote(self, request):
        """Casts the user's vote (thumps up - down).

        :param request: The web request.
        """
        try:
            auth_token = request.cookies.get('ragit_auth_token')
            user_name = request.cookies.get('user_name')
            Globals.validate_token(auth_token, user_name)
        except AuthenticationError:
            return web.HTTPFound('/login')
        try:
            data = await request.json()
            message_id = data.get('message_id')
            vote = data.get('vote')

            if vote == 1:
                UserRegistry.set_thumps_up(message_id)
            elif vote == 0:
                UserRegistry.set_thumps_down(message_id)

            return web.json_response(
                {
                    "response": "ok"
                }
            )
        except Exception as ex:
            return web.json_response({"response": str(ex)})

    @web_handler
    async def signup_new_acount(self, request):
        """Creates a new account

        :param request: The web request.
        """
        data = await request.post()  # Get the POST data as a dictionary
        user_name = data.get("user_name")
        password = data.get("password")
        email = data.get("email")
        try:
            UserRegistry.add_new_user(user_name, email, password)

        except common.MyGenAIException:
            return web.HTTPFound('/login')

    @web_handler
    async def login_screen(self, request):
        """Displays the login page.

        :param request: The web request.
        """
        try:
            auth_token = request.cookies.get('ragit_auth_token')
            user_name = request.cookies.get('user_name')
            Globals.validate_token(auth_token, user_name)
        except AuthenticationError:
            template = _JINJA_ENV.get_template('login.html')
            txt = template.render(host=request.host)
            logger.info("Serving login page.")
            return web.Response(
                body=txt.encode(),
                content_type='text/html'
            )
        else:
            return web.HTTPFound('/ragit')

    @web_handler
    async def login_validate(self, request):
        """Validates login credentials.

        :param request: The web request.
        """
        data = await request.post()  # Get the POST data as a dictionary
        user_name = data.get("user_name")
        password = data.get("password")

        try:
            UserRegistry.validate_password(user_name, password)
            response = aiohttp.web.HTTPFound('/ragit')
            auth_token = Globals.generate_token(user_name)
            response.set_cookie('ragit_auth_token', auth_token)
            response.set_cookie('user_name', user_name)
            return response
        except common.MyGenAIException:
            return web.HTTPFound('/login')


def initialize():
    """Initializes the environment."""
    common.init_settings()
    collection_name = os.environ.get("RAG_COLLECTION")
    if not collection_name:
        try:
            collection_name = sys.argv[1]
        except IndexError:
            raise ValueError("You must provide a valid collection name.")
    print(f"Loading vector db, using collection {collection_name}")
    Globals.rag_manager = rag_mgr.RagManager(collection_name)
    response = Globals.rag_manager.query("what is this about?")
    print("Loading vector db done..", response)
    UserRegistry.set_rag_collection_name(collection_name)
    UserRegistry.create_db_if_needed()


def run():
    """Runs the backend service."""
    initialize()
    app = web.Application()
    ragit_handler = RagitHandler()
    app.add_routes(
        [
            web.get('/', ragit_handler.default_handler),
            web.get('/login', ragit_handler.login_screen, name="login"),
            web.post('/login', ragit_handler.login_validate),
            web.get('/ragit', ragit_handler.main_page_handler),
            web.post('/ragit', ragit_handler.query_handler),
            web.get('/signup', ragit_handler.signup_screen),
            web.post('/signup', ragit_handler.signup_new_acount),
            web.post('/vote', ragit_handler.vote),

        ]
    )

    app_name = _CONFIGURATION.settings["web_service"]["name"]
    port = os.environ.get("SERVICE_PORT") or _DEFAULT_PORT
    port = int(port)
    app.router.add_static('/static', _PATH_TO_STATIC)
    logger.info(f"Starting {app_name} on port {port}")
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    run()
