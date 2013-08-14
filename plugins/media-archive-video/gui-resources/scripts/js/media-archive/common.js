define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/common'),
    config.guiJs('media-archive-video', 'models/video-data'),
    config.guiJs('media-archive-video', 'models/video-info'),
    config.guiJs('media-archive-video', 'models/video-info-list'),
    'tmpl!media-archive-video>media-archive/view',
    'tmpl!media-archive-video>media-archive/edit'
],
function($, superdesk, giz, base, VideoData, VideoInfo, VideoInfoList)
{
    var 
    // view details view
    View = base.view.extend
    ({
        getModel: function()
        {
            this.model = new VideoData(VideoData.prototype.url.get()+'/'+this.model.get('Id'));
            return this.model;
        },
        tmpl: 'media-archive-video>media-archive/view',
        feedTemplate: function()
        {
            var data = base.edit.prototype.feedTemplate.call(this),
                metas = [];
            this.model.get('VideoInfo').each(function(){ metas.push(this.feed()); });
            data.Meta = metas;
            return data;
        }
    }),
    // edit view
    Edit = base.edit.extend
    ({
        tmpl: 'media-archive-video>media-archive/edit',
        feedTemplate: View.prototype.feedTemplate,
        getModel: View.prototype.getModel,
        getInfoNode: function()
        {
            return this.model.get('VideoInfo');
        },
        getNewMetaInfo: function()
        {
            return new VideoInfo;
        }
    });
    return {edit: Edit, view: View};
});

