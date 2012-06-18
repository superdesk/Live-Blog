define(['gizmo', 
        'gui/superdesk/livedesk/scripts/js/models/collaborator-post',
        'gui/superdesk/livedesk/scripts/js/models/source'], 
function(giz, CollaboratorPost, Source)
{
    return giz.Model.extend({ defaults:{ Post: CollaboratorPost, Source: Source }});
});