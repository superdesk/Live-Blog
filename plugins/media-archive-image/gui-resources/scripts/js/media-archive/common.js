define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/common'),
    config.guiJs('media-archive-image', 'models/image-data'),
    config.guiJs('media-archive-image', 'models/image-info'),
    config.guiJs('media-archive-image', 'models/image-info-list'),
    'tmpl!media-archive-image>media-archive/view',
    'tmpl!media-archive-image>media-archive/edit'
],
function($, superdesk, giz, base, ImageData, ImageInfo, ImageInfoList)
{
    var 
    // vide details view
    View = base.view.extend
    ({
        getModel: function()
        {
            this.model = new ImageData(ImageData.prototype.url.get()+'/'+this.model.get('Id'));
            return this.model;
        },
        tmpl: 'media-archive-image>media-archive/view',
        feedTemplate: function()
        {
            var data = base.edit.prototype.feedTemplate.call(this),
                metas = [];
            this.model.get('ImageInfo').each(function(){ metas.push(this.feed()); });
            data.Meta = metas;
            return data;
        }
    }),
    // edit view
    Edit = base.edit.extend
    ({
        tmpl: 'media-archive-image>media-archive/edit',
        feedTemplate: View.prototype.feedTemplate,
        getModel: View.prototype.getModel,
        getInfoNode: function()
        {
            return this.model.get('ImageInfo');
        },
        getNewMetaInfo: function()
        {
            return new ImageInfo;
        }
    });
    return {edit: Edit, view: View};
});

