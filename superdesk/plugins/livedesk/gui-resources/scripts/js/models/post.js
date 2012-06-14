define(['gizmo', 'gui/superdesk/livedesk/scripts/js/models/collaborator'], function(giz, Collaborator)
{
    return giz.Model.extend({ defaults:{ Author: Collaborator }})
});