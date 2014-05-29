from requests import Session

from liveblog_helpers import reset_app
from liveblog_fixtures import upload_fixtures
from settings import SERVER_URL, PRINT_PAYLOAD, PRINT_URL, PRINT_HEADERS


def before_all(context):
    context.server_url = SERVER_URL.rstrip('/')
    context.session = Session()
    context.print_url = PRINT_URL
    context.print_payload = PRINT_PAYLOAD
    context.print_headers = PRINT_HEADERS
    context.template_variables = {}


def before_feature(context, feature):
    if feature.name == 'Embed':
        pass


def before_scenario(context, scenario):
    if 'skip' in scenario.tags:
        scenario.steps = []
        scenario.mark_skipped()
    reset_app(context)
    upload_fixtures(context)
