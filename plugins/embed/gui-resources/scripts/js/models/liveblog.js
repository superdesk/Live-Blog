'use strict';

define([
    'underscore',
    'models/base-model'
], function(_, BaseModel) {
    return BaseModel.extend({
        initialize: function() {
            var data = _.clone(liveblog);
            data.servers = _.clone(liveblog.servers);
            data.servers.rest = liveblog.browserUrl(data.servers.rest);
            if (data.servers.frontend) {
                data.servers.frontend = liveblog.browserUrl(data.servers.frontend);
            }
            this.set(data);
        }
    });
});
