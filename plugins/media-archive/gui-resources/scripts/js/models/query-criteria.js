define([ 'gizmo/superdesk' ],
function(giz)
{
    return giz.Model.extend
    ({ 
        url: new giz.Url('Archive/QueryCriteria'),
        hash: function()
        {
            return this.data.Key || this._getClientHash();
        }
    });
});