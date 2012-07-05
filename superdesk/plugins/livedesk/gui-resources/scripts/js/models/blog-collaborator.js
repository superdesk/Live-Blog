define(['gizmo/superdesk', 
        'gui/superdesk/livedesk/scripts/js/models/collaborator'], 
function(giz, Collaborator)
{
    var BlogCollaborator = giz.Collection.extend({ model: Collaborator });  
    // Blog Collaborator list
    return BlogCollaborator;
    
});