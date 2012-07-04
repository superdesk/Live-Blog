define(['gizmo/superdesk', 
        'gui/superdesk/livedesk/scripts/js/models/collaborator'], 
function(giz, Collaborator)
{
    // Blog Collaborator list
    return giz.Collection.extend({ model: Collaborator });
});