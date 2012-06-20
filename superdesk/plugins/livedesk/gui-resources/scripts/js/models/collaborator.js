define(['gizmo',
        'gui/superdesk/livedesk/scripts/js/models/post',
        'gui/superdesk/livedesk/scripts/js/models/source'], 
function(giz, Post, Source)
{
    return giz.Model.extend
    ({ 
        defaults:
        { 
            Post: [Post],
            PostPublished: [Post],
            PostUnpublished: [Post],
            Source: Source 
        }
    });
});