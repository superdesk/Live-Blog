define
([
    'gizmo/superdesk'
], 
function(giz, User)
{ 
    return giz.Model.extend
    ({
        url: new giz.Url('Desk/Task'),
    });
});