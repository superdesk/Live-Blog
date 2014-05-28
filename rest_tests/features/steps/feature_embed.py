from behave import given

from wooper.expect import expect_status
from wooper.rest import get_id_from_href

from liveblog_helpers import POST


@given('{number:n} posts were published to embed')
def step_impl_embed_pulish_posts(context, number):
    for i in range(number):
        # add post
        POST(
            context,
            '/my/LiveDesk/Blog/1/Post', {
                'Meta': '{}',
                'Content': 'test' + str(i),
                'Type': 'normal',
                'Creator': '1'})
        expect_status(context.response, 201)
        last_id = get_id_from_href(context)

        # publish post
        POST(
            context,
            '/my/LiveDesk/Blog/1/Post/{id}/Publish'.format(id=last_id))
        expect_status(context.response, 201)
