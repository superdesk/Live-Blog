define([ 'gizmo/superdesk' ],
function(giz, MetaType)
{
	return giz.Collection.extend({ model: MetaType, href: new giz.Url('Archive/MetaType') })
});