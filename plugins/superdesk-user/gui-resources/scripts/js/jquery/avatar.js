define('jquery/avatar', ['utils/str', 'jquery', 'gizmo', 'jquery/utils', 'jquery/md5'], function(str, $, gizmo) {
    var counter = 0,
        gravatar = {
        url: '//gravatar.com/avatar/%(md5)s?r=%(rate)s&s=%(size)s&d=%(default)s&%(forcedefault)s',
        defaults: {
            rate: 'pg',
            size: 48,
            sizeText: 'large',
            metaDataKey: 'MetaData',
            default: encodeURIComponent('images/avatar_default_collaborator.png'),
            forcedefault: '',
            key: 'Avatar',
            needle: 'Person.EMail'
        },
        parse: function(data, needle) 
        {
            if(!data) return;
            if( typeof needle == 'undefined' ) needle = this.defaults.needle;
            
            if(data instanceof gizmo.Model)
            {
                var self = this,
                    retData = data.feed(),
                    lookInto = needle.split('.'),
                    meta = data,
                    dfdMeta = new $.Deferred;
                lookInto.pop();
                for( var i=0; i<lookInto.length; i++)
                {
                    meta = meta.get(lookInto[i]);
                    if( !(meta instanceof gizmo.Model) ) return retData; // can't go down the chain
                    if(i == lookInto.length-1) 
                    {
                        meta.sync().done(function(){ dfdMeta.resolve(); });
                        continue;
                    }
                    meta.sync();
                }
                if(!lookInto.length) dfdMeta.resolve();
                dfdMeta.__imgAvatarId = counter;
                retData[this.defaults.key] = '<img data-avatar-id="'+(counter++)+'" src="'+this.defaults.default+'" />';
                dfdMeta.done(function()
                {
                    meta = meta.get(self.defaults.metaDataKey);
                    if(!meta) return;
                    var img = retData[self.defaults.key],
                        count = this.__imgAvatarId;
                    meta.sync({ data: { thumbSize: self.defaults.sizeText }}).done(function()
                    {
                        $('[data-avatar-id="'+count+'"]').attr('src', meta.get('Thumbnail').href);
                    })
                    .fail(function()
                    {
                        self._parse(retData, needle, count);
                    });
                });
                
                return retData;
            }
            return this._parse(data, needle);
        },
        _parse: function(data, needle, imgId)
        {
            var self = this,
			arr = needle.split('.'),
			searchKey = arr[0],
            searchValue = arr[1];
            $.each(data, function(key, value){
				if((key === searchKey) && (searchValue!==undefined) && ( $.isDefined(value[searchValue]))) {
					if(imgId) $('[data-avatar-id="'+imgId+'"]').attr('src', self.get(value[searchValue]));
					else this[self.defaults.key] = self.get(value[searchValue]);
                }
                if($.isObject(value) || $.isArray(value)) {
                    self._parse(value, needle, imgId);
                }
            });
            return data;
        },
		get: function(value) {
            var self = this;
            if(!$.isString(value))
                return value;
			return str.format(self.url,$.extend({}, self.defaults, { md5: $.md5($.trim(value.toLowerCase()))}));
		}
    };
    $.avatar  = gravatar;
});