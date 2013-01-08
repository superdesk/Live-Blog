define('jquery/avatar', ['utils/str', 'jquery', 'gizmo', 'jquery/utils', 'jquery/md5'], function(str, $, gizmo) {
    var counter = 0,
        gravatar = {
        url: '//gravatar.com/avatar/%(md5)s?r=%(rate)s&s=%(size)s&d=%(default)s&%(forcedefault)s',
        defaults: {
            rate: 'pg',
            size: 48,
            sizeText: 'large',
            default: encodeURIComponent('images/avatar_default_collaborator.png'),
            forcedefault: '',
            key: 'Avatar',
            needle: 'Person.EMail'
        },
        parse: function(data, needle) {
            if(!data) return;
            
            if(data instanceof gizmo.Model)
            {
                var retData = data.feed(),
                    meta = data.get('MetaData');
                if(!meta) return;
                meta.__imgAvatarId = counter;
                retData[this.defaults.key] = '<img data-avatar-id="'+(counter++)+'" src="'+this.defaults.default+'" />';
                var img = retData[this.defaults.key];
                meta.sync({ data: { thumbSize: this.defaults.sizeText }}).done(function()
                {
                    $('[data-avatar-id="'+meta.__imgAvatarId+'"]').attr('src', meta.get('Thumbnail').href);
                    delete meta.__imgAvatarId;
                });
                return retData;
            }
            
            if(!needle) needle = this.defaults.needle;
            var self = this,
			arr = needle.split('.'),
			searchKey = arr[0],
            searchValue = arr[1];
            $.each(data, function(key, value){
				if((key === searchKey) && (searchValue!==undefined) && ( $.isDefined(value[searchValue]))) {
					this[self.defaults.key] = self.get(value[searchValue]);
                }
                if($.isObject(value) || $.isArray(value)) {
                    self.parse(value,needle);
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