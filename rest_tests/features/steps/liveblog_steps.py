import json
import behave
from behave import when

from wooper.steps import process_common_templates

from liveblog_helpers import liveblog_request


def request(context, method, uri, data=None, *args, **kwargs):
    uri = process_common_templates(uri, context)
    if not data:
        if 'text' in context:
            if context.text:
                data = process_common_templates(context.text, context)
        else:
            data = ''
    liveblog_request(
        context, method, uri, *args, data=data, **kwargs)

# ============================================================================
behave.use_step_matcher('re')
METHODS_RE = '(?P<method>GET|POST|PUT|PATH|DELETE)'


@when(METHODS_RE + ' (?P<uri>.*) with headers')
def step_impl_request_with_headers(context, method, uri):
    headers = json.loads(context.text)
    request(context, method, uri, headers=headers)


@when(METHODS_RE + ' (?P<uri>.*)')
def step_impl_request(context, method, uri):
    request(context, method, uri)


# ============================================================================
behave.use_step_matcher('parse')

# normal steps will be here
