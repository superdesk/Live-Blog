define([ 
	'gizmo/superdesk',
	config.guiJs('livedesk', 'models/blogtype') 
], function( Gizmo ) {

    return Gizmo.Collection.extend({
    	url: new Gizmo.Url('LiveDesk/BlogType'),
    	model: Gizmo.Register.BlogType 
    }, { register: 'BlogTypes' } );

});