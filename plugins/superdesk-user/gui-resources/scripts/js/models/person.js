define([ 'gizmo/superdesk' ],
function(Gizmo)
{
    // Person (1-1 User)
    return Gizmo.Model.extend({ url: Gizmo.Url('/Person') });
});