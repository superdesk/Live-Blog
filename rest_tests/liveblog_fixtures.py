import uuid

from wooper.rest import get_id_from_href
from wooper.expect import expect_status

from liveblog_helpers import POST


def fixture_embed(context):
    # add post
    POST(context,
         '/my/LiveDesk/Blog/1/Post', {
             'Meta': '{}',
             'Content': 'test{}' + str(uuid.uuid4()),
             'Type': 'normal',
             'Creator': '1'})
    expect_status(context.response, 201)
    last_id = get_id_from_href(context)
    # publish post
    POST(context,
         '/my/LiveDesk/Blog/1/Post/{id}/Publish'.format(id=last_id))
    expect_status(context.response, 201)
    # update last_id
    context.template_variables['last_id'] = last_id


def upload_fixtures(context, number=1):
    if context.scenario.feature.name == 'Embed':
        for i in range(number):
            fixture_embed(context)
