define(['gizmo/superdesk',
    config.guiJs('livedesk', 'models/posts'),
    config.guiJs('livedesk', 'models/source'),
    config.guiJs('livedesk', 'models/person')], 
function(giz, Posts, Source, Person)
{
    // Collaborator
    return giz.Model.extend
    ({ 
        defaults:
        { 
            Post: Posts,
            PostPublished: Posts,
            PostUnpublished: Posts,
            Source: Source,
            Person: Person
        }
    }, { register: 'Collaborator' } );
});