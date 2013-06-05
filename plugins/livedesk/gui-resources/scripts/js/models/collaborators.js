define(['jquery', 'gizmo/superdesk', config.guiJs('livedesk', 'models/collaborator')], 
function($, Gizmo, Collaborator)
{
    return Gizmo.Collection.extend({ 
        _config: { limit: 1000 },
        url: new Gizmo.Url('Superdesk/Collaborator'),
        add: function(data){
           var self = this,
                dataAdapter = function()
                { 
                    return self.syncAdapter.request.apply(self.syncAdapter, arguments); 
                }, dfd = $.Deferred();
            for( var i = 0, count = data.length; i < count; i++) {
                ret = dataAdapter(this.href+data[i].get('Id')+'/Add').update({});
            }
            return ret;
        },
        remove: function(data) {
           var self = this,
                dataAdapter = function()
                { 
                    return self.syncAdapter.request.apply(self.syncAdapter, arguments); 
                }, dfd = $.Deferred();
            for( var i = 0, count = data.length; i < count; i++) {
                ret = dataAdapter(this.href+data[i].get('Id')+'/Remove').remove();
            }
            return ret;         
        },
        model: Collaborator
    }, { register: 'Collaborators' } );
});