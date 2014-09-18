define([ 'gizmo/superdesk'],
function(Gizmo) 
{
    // Blog
    return Gizmo.Model.extend
    ({
		url: new Gizmo.Url('GeneralSetting')
    }, 
    { register: 'GeneralSetting' } );
});
