define([ 'gizmo/superdesk', config.guiJs('media-archive', 'models/meta-info-list'), config.guiJs('media-archive', 'models/meta-info') ],
function(giz, MetaInfoList, MetaInfo)
{
    return giz.Model.extend
    ({  
        defaults: 
        {
            MetaInfo: MetaInfo
        },
        refresh: function()
        {
            var metaInfo = this;
            this.sync({data: {thumbSize: 'medium'}}).done(function()
            {
                metaInfo.get('MetaInfo').xfilter('*').sync().done(function()
                {
                    metaInfo.triggerHandler('full-refresh', self);
                });
            });
        }
    });
});