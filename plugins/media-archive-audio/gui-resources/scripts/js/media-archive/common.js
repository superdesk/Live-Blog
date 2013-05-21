define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/common'),
    config.guiJs('media-archive-audio', 'models/audio-data'),
    config.guiJs('media-archive-audio', 'models/audio-info'),
    config.guiJs('media-archive-audio', 'models/audio-info-list'),
    'tmpl!media-archive-audio>media-archive/view',
    'tmpl!media-archive-audio>media-archive/edit'
],
function($, superdesk, giz, base, AudioData, AudioInfo, AudioInfoList)
{
    var 
    // view details view
    View = base.view.extend
    ({
        getModel: function()
        {
            this.model = new AudioData(AudioData.prototype.url.get()+'/'+this.model.get('Id'));
            return this.model;
        },
        tmpl: 'media-archive-audio>media-archive/view',
        feedTemplate: function()
        {
            var data = base.edit.prototype.feedTemplate.call(this),
                metas = [];
            this.model.get('AudioInfo').each(function(){ metas.push(this.feed()); });
            data.Meta = metas;
            return data;
        }
    }),
    // edit view
    Edit = base.edit.extend
    ({
        tmpl: 'media-archive-audio>media-archive/edit',
        feedTemplate: View.prototype.feedTemplate,
        getModel: View.prototype.getModel,
        getInfoNode: function()
        {
            return this.model.get('AudioInfo');
        },
        getNewMetaInfo: function()
        {
            return new AudioInfo;
        }
    });
    // remove view
    Remove = base.remove.extend
    ({
        getInfoCollection: function()
        {
            return giz.Auth(new AudioInfoList(this.model.get('MetaInfo').href.replace('MetaInfo', 'AudioInfo').replace('MetaData', 'AudioData')));
        }
    });
    return {edit: Edit, view: View, remove: Remove};
});

