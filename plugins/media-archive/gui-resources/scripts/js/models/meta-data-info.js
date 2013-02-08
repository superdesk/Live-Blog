define([ 'gizmo/superdesk',
         config.guiJs('media-archive', 'models/meta-data'),
         config.guiJs('media-archive', 'models/meta-info'),
         config.guiJs('media-archive', 'models/language')],
function(giz, MetaData, MetaInfo, Language)
{
    return giz.Model.extend
    ({ 
        url: new giz.Url('Archive/MetaDataInfo/Query'),
        defaults:
        {
            Language: Language
        },
        /*!
         * make and return MetaData model
         */
        getMetaData: function()
        {
            var meta = new MetaData(MetaData.prototype.url.get()+'/'+this.get('Id'));
            meta.set('Id', this.get('Id'));
            meta._changed = false;
            return meta;
        },
        /*!
         * make and return MetaInfo model
         */
        getMetaInfo: function()
        {
            var meta = new MetaInfo(MetaInfo.prototype.url.get()+'/'+this.get('Id'));
            meta.set('Id', this.get('Id'));
            meta._changed = false;
            return meta;
        },
        hash: function()
        {
            return this.data.Id || this._getClientHash();
        }
    });
});