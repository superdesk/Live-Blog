define([
	'gizmo/superdesk',
	config.guiJs('livedesk', 'models/posts')
], function( Gizmo )
{
    return Gizmo.Model.extend({
    	url: new Gizmo.Url('LiveDesk/BlogType'),
    	defaults: { 
    		BlogTypePost: Gizmo.Register.Posts
    	},
    	syncParse: function(data){
    		var self = this,
                ret = self.set(data);
            if(self._new) {
                return ret.xfilter('Id').sync().done(function(data){
                    self._parseHash(data);
                    self.Class.triggerHandler('add', self);
                });

            } else {
    		  return ret.sync();
            }
    	}
	}, { register: 'BlogType' });
});