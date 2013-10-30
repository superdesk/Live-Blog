define(['gizmo/superdesk', config.guiJs('livedesk', 'models/sources')], function(Gizmo)
{
    return Gizmo.Collection.extend({
    	url: new Gizmo.Url('Data/Source'), 
    	model: Gizmo.Register.Source
    }, { register: 'Sources' } );
});