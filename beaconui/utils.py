import logging
import asyncio

from aiohttp import web, ClientSession
import async_timeout

LOG = logging.getLogger(__name__)

async def request(method, url, **kwargs):
    """Make a request through AIOHTTP."""
    timeout = kwargs.pop('timeout', None)
    try:
        async with async_timeout.timeout(timeout):
            async with ClientSession() as session:
                LOG.debug('%4s Request: %s', method, url)
                LOG.debug('Request Args: %s', kwargs)
                async with session.request(method, url, **kwargs) as response:
                    LOG.debug('Response type: %s', response.headers.get('CONTENT-TYPE'))
                    LOG.debug('Response: %s', response)
                    if response.status > 200:
                        raise web.HTTPBadRequest(reason=f'HTTP status code: {response.status}')
                    if 'json' in response.headers.get('CONTENT-TYPE'):
                        data = await response.json()
                    else:
                        data = await response.text()
                        data = dict(parse_qsl(data))
                    return data
    except asyncio.TimeoutError:
        raise web.HTTPBadRequest(reason='HTTP timeout')
    except Exception as e:
        LOG.debug('Exception: %s', e)
        return None
