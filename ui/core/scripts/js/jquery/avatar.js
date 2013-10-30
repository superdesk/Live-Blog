define('jquery/avatar', ['utils/str', 'jquery', 'jquery/utils', 'jquery/md5'], function(str, $) {
    var coreStyles = config.coreStyles("."),
    //coreStyles = coreStyles.indexOf('http') === -1? 'http:'+coreStyles : coreStyles;
    gravatar = {
        url: '//gravatar.com/avatar/%(md5)s?r=%(rate)s&s=%(size)s&d=%(default)s&%(forcedefault)s',
        defaults: {
            rate: 'pg',
            size: 48,
            default: encodeURIComponent(coreStyles+'/../../images/avatar_default_collaborator.jpg'),
            forcedefault: '',
            key: 'Avatar',
            needle: 'Person.EMail'
        },
        parse: function(data, needle, options) {
            if(!data) return;
            if(!needle) needle = this.defaults.needle;
            var self = this,
			arr = needle.split('.'),
			searchKey = arr[0],
            searchValue = arr[1];
            $.each(data, function(key, value){
				if((key === searchKey) && (searchValue!==undefined) && ( $.type(value[searchValue]) !== undefined)) {
					this[self.defaults.key] = self.get(value[searchValue]);
                }
                if($.isObject(value) || $.isArray(value)) {
                    self.parse(value,needle);
                }
            });
            return data;
        },
        set: function(data, needle, options){
            if(!needle) needle = this.defaults.needle;
            var self = this,
            arr = needle.split('.'),
            searchKey = arr[0],
            searchValue = arr[1];
            if((data[searchKey]) && (searchValue!==undefined) && ( $.type(data[searchKey][searchValue]) !== undefined )) {
                data[searchKey][self.defaults.key] = self.get(data[searchKey][searchValue],options);
            }            
        },
		get: function(value,options) {
            var self = this;
            if(!options)
                options = {};
            if($.type(value) !== 'string')
                return value;
			return str.format(self.url,$.extend({}, self.defaults, options, { md5: $.md5($.trim(value.toLowerCase()))}));
		}
    };
    $.avatar  = gravatar;
});