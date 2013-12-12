define([ 'gizmo/superdesk', 
         config.guiJs('media-archive', 'models/meta-info-list')],
function(giz, MetaInfoList)
{
    return giz.Model.extend
    ({  
        url: new giz.Url('Archive/MetaData'),
        defaults: 
        {
            MetaDataMetaInfo: MetaInfoList
        },
        infoNode: 'MetaDataMetaInfo',
        refresh: function(thumbSize)
        {
            var self = this;
            this.sync({data: {thumbSize: thumbSize || 'medium'}}).done(function()
            {
                self.get(self.infoNode).xfilter('MetaData.*').sync().done(function()
                {
                    self.triggerHandler('full-refresh', self);
                });
            });
        }
    });
});