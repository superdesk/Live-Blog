define(['utils/str', 'jquery', 'jquery-path/utils', 'jquery-path/md5'], function(str, $) {
    var gravatar = {
        url: '//gravatar.com/avatar/%(md5)s?r=%(rate)s&s=%(size)s&d=%(default)s&%(forcedefault)s',
        defaults: {
            rate: 'pg',
            size: 48,
            default: encodeURIComponent('images/avatar_default_collaborator.png'),
            forcedefault: '',
            key: 'Avatar',
            needle: 'Person.EMail'
        },
        parse: function(data, needle) {
            if(!data) return;
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