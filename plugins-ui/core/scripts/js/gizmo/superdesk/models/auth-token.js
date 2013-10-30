define(['gizmo/superdesk'], function(Gizmo)
{
    return Gizmo.Model.extend({ url: new Gizmo.Url('Security/Authentication') });
});