from requests import Session

from wooper.rest import get_id_from_href
from wooper.expect import expect_status

from liveblog_helpers import reset_app, POST
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

    if scenario.feature.name == 'Embed':
        # add post
        POST(
            context,
            '/my/LiveDesk/Blog/1/Post', {
                'Meta': '{}',
                'Content': 'test',
                'Type': 'normal',
                'Creator': '1'
            })
        expect_status(context.response, 201)
        last_id = get_id_from_href(context)

        # publish post
        POST(
            context,
            '/my/LiveDesk/Blog/1/Post/{id}/Publish'
            .format(id=last_id))
        expect_status(context.response, 201)

        context.template_variables['last_id'] = last_id
