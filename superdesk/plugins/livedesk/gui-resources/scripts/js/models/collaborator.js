define(['gizmo/superdesk',
        'gui/superdesk/livedesk/scripts/js/models/post',
        'gui/superdesk/livedesk/scripts/js/models/source',
        'gui/superdesk/livedesk/scripts/js/models/person'], 
function(giz, Post, Source, Person)
{
    // Collaborator
    var Collaborator = giz.Model.extend
    ({ 
        defaults:
        { 
            Post: giz.Collection.extend({ model: Post }),
            PostPublished: giz.Collection.extend({ model: Post }),
            PostUnpublished: giz.Collection.extend({ model: Post }),
            Source: Source,
            Person: Person
        }
    });
    return Collaborator;
});