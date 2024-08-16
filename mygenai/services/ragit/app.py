"""Exposes the Sibyl Main web page."""

import functools
import logging
import os

import aiohttp
import aiohttp.web as web
import jinja2

logger = logging.getLogger("ragit")

_PORT = 13131

_JINJA_ENV = jinja2.Environment(
    loader=jinja2.PackageLoader(
        'templates',
        'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

_CURR_DIR = os.path.dirname(os.path.realpath(__file__))
_PATH_TO_STATIC = os.path.join(_CURR_DIR, 'static')

APP_NAME = "ragit"


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
        except Exception as ex:
            logger.exception(ex)
            raise aiohttp.web.HTTPInternalServerError()

    return _inner


class Handler:
    """Implements all the web handlers used from the service."""

    @web_handler
    async def main_page_handler(self, request):
        """Displays the main page.

        :param request: The web request.
        """
        template = _JINJA_ENV.get_template('index.html')
        title = "Chat Bot"
        desc = "Specializes in  Alzheimer's diagnosis with MRI using AI."
        txt = template.render(host=request.host, title=title, description=desc)
        logger.info("Serving main page.")
        return web.Response(
            body=txt.encode(),
            content_type='text/html'
        )

    @web_handler
    async def query_handler(self, request):
        data = await request.json()
        query = data.get('query')
        return web.json_response({"response": "not ready yet."})


def run():
    """Runs the backend service."""
    app = web.Application()
    handler = Handler()
    app.add_routes(
        [
            web.get('/', handler.main_page_handler),
            web.post('/', handler.query_handler),
        ]
    )
    app.router.add_static('/static', _PATH_TO_STATIC)
    logger.info(f"Starting {APP_NAME} on port {_PORT}")
    web.run_app(app, port=_PORT)


if __name__ == '__main__':
    run()
