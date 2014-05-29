import json

from wooper.rest import request
from wooper.steps import process_common_templates

from auth import get_token


def liveblog_request(context, method, uri, data=None,
                     with_auth=True, token=None, add_server=True,
                     **kwargs):
    # payload
    if not data:
        if 'text' in context:
            if context.text:
                data = process_common_templates(context.text, context)
        else:
            data = ''
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)
    # uri
    uri = process_common_templates(uri, context)
    # auth
    if 'headers' in kwargs:
        headers = kwargs.pop('headers')
    else:
        headers = {}
    if with_auth:
        if not token:
            if not context.token:
                context.token = get_token(session=context.session)
            token = context.token
        headers.update({'Authorization': token})
    # request itself
    request(
        context, method, uri,
        data=data, headers=headers, add_server=add_server,
        **kwargs)


def GET(context, uri, *args, **kwargs):
    liveblog_request(context, 'GET', uri, *args, **kwargs)


def POST(context, uri, *args, **kwargs):
    liveblog_request(context, 'POST', uri, *args, **kwargs)


def PATCH(context, uri, *args, **kwargs):
    liveblog_request(context, 'PATCH', uri, *args, **kwargs)


def PUT(context, uri, *args, **kwargs):
    liveblog_request(context, 'PUT', uri, *args, **kwargs)


def DELETE(context, uri, *args, **kwargs):
    liveblog_request(context, 'DELETE', uri, *args, **kwargs)


def reset_app(context):
    PUT(
        context,
        '/Tool/TestFixture/default', {
            'Name': 'default',
            'ApplyOnDatabase': True,
            'ApplyOnFiles': True},
        with_auth=False)
    context.token = get_token(session=context.session)
