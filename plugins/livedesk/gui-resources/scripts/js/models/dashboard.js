define([ 'gizmo/superdesk'],
function(Gizmo) 
{
    // UrlInfo
    return Gizmo.Model.extend
    ({
        // TODO this is not the real model path. should be LiveDesk/Blog
		url: new Gizmo.Url('LiveDesk/Blog/Live'),
        getInfoSync: function(url){

            var getInfoHref = this.url.get();
            var
                self = this,
                dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(getInfoHref).read();
            return ret;     
        }
    }, 
    { register: 'LiveBlogs' } );
});