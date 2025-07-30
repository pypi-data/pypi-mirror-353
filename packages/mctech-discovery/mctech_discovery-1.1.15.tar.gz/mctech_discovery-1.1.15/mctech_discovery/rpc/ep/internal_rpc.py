from __future__ import absolute_import
import httpx
from functools import partial

from ..web_error import WebError
from ..request_context import RequestContext, EndPoint
from ...discovery import discovery_client as client


def _create_request_option(context: RequestContext, url: str):
    option = {
        'method': context.invoker.method,
        'url': url,
        'body': context.invoker.body,
        'headers': {
            'accept': 'application/json,*/*',
            'accept-encoding': 'gzip, deflate',
            'user-agent': 'nodejs rest client',
            'content-type': 'application/json',
            # 表示异步调用
            'x-client-ajax': 'true'
        },
        'timeout': httpx.USE_CLIENT_DEFAULT
    }
    # if context.timeout:
    #     option['timeout'] = context.timeout / 1000
    option['headers'].update(context.headers)
    context.process_request_option(option)
    return option


async def _walk_using_urllib(context: RequestContext, url: str) -> httpx.Response:  # noqa
    option = _create_request_option(context, url)
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        content_type = option['headers'].get('content-type') or ''
        kwargs = {}
        body = option["body"]
        if isinstance(body, (str, bytes)):
            kwargs['content'] = body
        # elif isinstance(body, io.IOBase):
        #     pass
        else:  # Any type
            if content_type.lower().find('json'):
                kwargs['json'] = body
            else:
                kwargs['data'] = body

        res: httpx.Response = await client.request(
            method=option["method"],
            url=option["url"],
            headers=option["headers"],
            timeout=option["timeout"],
            **kwargs)
        return res


async def _do_request(context: RequestContext, ep: EndPoint) -> httpx.Response:
    res: httpx.Response
    if ep:
        url = "http://%s:%d%s" % (ep.host, ep.port, context.path_and_query)
        res = await _walk_using_urllib(context, url)
    else:
        res = await client.client.walk_nodes(
            app_name=context.service.service_id,
            service=context.path_and_query,
            walker=partial(_walk_using_urllib, context)
        )

    if res.status_code >= 400:
        timeout = context.timeout if context.timeout else -1
        service = context.service
        invoker = context.invoker

        message = "%s --> %s --> [timeout:%ds, cost: %fs] [%s] [%s] %s" % (
            res.reason_phrase, res.text, timeout, res.elapsed.total_seconds(),  # noqa
            service.service_id, invoker.method, context.url)
        err = WebError(message, status=res.status_code)
        context.resolve_error(res, err)
        raise err

    return res


async def execute(context: RequestContext, ep: EndPoint):
    '''
    :return Awaitable[JsonObject, str, http.Response] 返回值可以是 json，str 或 httpx.Response
    '''

    res: httpx.Response = await _do_request(context, ep)
    content_type = res.headers.get('content-type') or ''

    if content_type.find('json') >= 0:
        return res.json()
    elif content_type.find('text/') >= 0:
        return res.text
    return res


async def stream(context: RequestContext, ep: EndPoint):
    '''
    :return Awaitable[httpx.Response]
    '''

    res: httpx.Response = await _do_request(context, ep)
    return res


def ws(context: RequestContext, ep: EndPoint):
    if ep:
        url = "ws://%s:%d%s" % (ep.host, ep.port, context.path_and_query)
    else:
        ec = client.client
        app_name = context.service.service_id.upper()
        service = context.path_and_query
        node = ec.__get_available_service(app_name)
        url = ec.__generate_service_url(node, False, False)
        if service.startswith("/"):
            url = url + service[1:]
        else:
            url = url + service

    option = _create_request_option(context, url, False)
    from websocket import create_connection
    conn = create_connection(url=option["url"],
                             timeout=option["timeout"],
                             headers=option['headers']
                             )

    return conn
