define(['gizmo/superdesk',
        'livedesk/models/post',
        'livedesk/models/source',
        'livedesk/models/person'], 
function(Gizmo)
{
    // Collaborator
    return Gizmo.Model.extend
    ({ 
        defaults:
        { 
            Post: Gizmo.Collection.extend({ model: Gizmo.Model.Post }),
            PostPublished: Gizmo.Collection.extend({ model: Gizmo.Model.Post }),
            PostUnpublished: Gizmo.Collection.extend({ model: Gizmo.Model.Post }),
            Source: Gizmo.Model.Source,
            Person: Gizmo.Model.Person
        }
    }, { register: 'Collaborator' } );
});