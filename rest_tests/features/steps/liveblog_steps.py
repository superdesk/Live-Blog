import json
import behave
from behave import when

from liveblog_helpers import liveblog_request


# ============================================================================
behave.use_step_matcher('re')
METHODS_RE = '(?P<method>GET|POST|PUT|PATH|DELETE)'


@when(METHODS_RE + ' (?P<uri>.*) with headers')
def step_impl_request_with_headers(context, method, uri):
    headers = json.loads(context.text)
    liveblog_request(context, method, uri, headers=headers)


@when(METHODS_RE + ' (?P<uri>.*)')
def step_impl_request(context, method, uri):
    liveblog_request(context, method, uri)


# ============================================================================
behave.use_step_matcher('parse')

# normal steps will be here
