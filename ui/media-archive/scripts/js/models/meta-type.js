define([ 'gizmo/superdesk' ],
function(giz)
{
    return giz.Model.extend({ url: new giz.Url('Archive/MetaType') });
});