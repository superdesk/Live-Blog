define([ 'gizmo/superdesk'],
function(Gizmo) 
{
    // UrlInfo
    return Gizmo.Model.extend
    ({
        // TODO this is not the real model path. should be LiveDesk/Blog
		url: new Gizmo.Url('Tool/URLInfo'),
        getInfoSync: function(url){
            //temp fix to encode the '.' (dot) char
            //url = url.replace(/\./gi, '%2e');

            var getInfoHref = this.url.get()+'?url='+encodeURIComponent(url);
            var
                self = this,
                dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(getInfoHref).read();
            return ret;     
        }
    }, 
    { register: 'URLInfo' } );
});