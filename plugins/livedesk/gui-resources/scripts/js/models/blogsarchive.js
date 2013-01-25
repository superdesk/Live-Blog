define([ 'gizmo/superdesk'],
function(Gizmo) 
{
    // BLOGSArchive
    return Gizmo.Model.extend
    ({
        url: new Gizmo.Url('LiveDesk/Blog/?isLive=false&X-Filter=*'),

        getInfoSync: function(title, offset, limit, order){
            
            offset = typeof offset == undefined ? 0 : offset;
            limit = typeof limit == undefined ? 10 : limit;
            title = typeof title == undefined ? '%' : title;
            order = typeof order == 'undefined' ? 'createdOn' : order;

            //http://localhost:8080/resources/LiveDesk/Blog/?X-Filter=*&isLive=true&title.ilike=gen%%
            var params = '&title.ilike=' + encodeURIComponent('%' + title + '%') + '&limit=' + limit + '&offset=' + offset + '&asc=' + order;
            //console.log('params ', params);
            var getInfoHref = this.url.get() + params;
            var
                self = this,
                dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(getInfoHref).read();
            return ret;     
        }
    }, 
    { register: 'BLOGSArchive' } );
});