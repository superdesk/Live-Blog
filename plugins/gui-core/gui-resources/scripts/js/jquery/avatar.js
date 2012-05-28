define('jquery/avatar', ['utils/str', 'jquery', 'jquery/utils', 'jquery/md5'], function(str, $) {
    var gravatar = {
        url: '//gravatar.com/avatar/%(md5)s?r=%(rate)s&s=%(size)s&d=%(default)s&%(forcedefault)s',
        defaults: {
            rate: 'pg',
            size: 48,
            default: encodeURIComponent('http://liveblog.lab.sourcefabric.org/content/lib/core/images/avatar_default_collaborator.png'),
            forcedefault: '',
            key: 'Avatar',
            needle: 'Person.EMail'
        },
        parse: function(data, needle) {
            if(!data) return;
            var self = this;
            if(!needle) needle = self.defaults.needle;
            var arr = needle.split('.');
            var searchKey = arr[0];
            var searchValue = arr[1];
            $.each(data, function(key, value){
                if((key === searchKey) && ( $.isDefined(value[searchValue]))) {
                    this[self.defaults.key] = str.format(self.url,$.extend({}, self.defaults, { md5: $.md5($.trim(value.EMail.toLowerCase()))}));
                }
                if($.isObject(value) || $.isArray(value)) {
                    self.parse(value,needle);
                }
            });
            return data;
        },
    };
    $.avatar  = gravatar;
});