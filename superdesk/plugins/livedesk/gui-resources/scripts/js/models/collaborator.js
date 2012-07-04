define(['gizmo',
        'gui/superdesk/livedesk/scripts/js/models/post',
        'gui/superdesk/livedesk/scripts/js/models/source',
        'gui/superdesk/livedesk/scripts/js/models/person'], 
function(giz, Post, Source, Person)
{
    // Collaborator
    return giz.Model.extend
    ({ 
        defaults:
        { 
            Post: new giz.Collection(Post),
            PostPublished: new giz.Collection(Post),
            PostUnpublished: new giz.Collection(Post),
            Source: Source,
            Person: Person
        }
    });
});