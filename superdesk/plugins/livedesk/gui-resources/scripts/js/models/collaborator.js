define(['gizmo', 'gui/superdesk/livedesk/scripts/js/models/collaborator-post'], function(giz, CollaboratorPost)
{
    return giz.Model.extend({ defaults:{ Post: CollaboratorPost }});
});