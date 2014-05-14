'use strict';

define([
    'underscore',
    'models/base-model'
], function(_, BaseModel) {
    // @TODO: refactor url-href in a much cleaner way,
    //   also add the with the liveblog browserUrl method.
    var browserUrl = function(urlString) {
        var regxProtocol = /^(http[s]?:)?\/{2}/,
            regxServer = /^(http[s]?:)?\/{2}([0-9.\-A-Za-z]+)(?::(\d+))?/;
        urlString = regxProtocol.test(urlString) ? urlString : '//' + urlString;
        urlString = urlString.replace(regxServer, function(all, protocol, hostname, port) {
            return '//' +
                    hostname +
                    ((port && port !== '80' && port !== '443') ? ':' + port : '');
        });
        return urlString;
    };

    return BaseModel.extend({
        initialize: function() {
            var data = _.clone(liveblog);
            data.servers = _.clone(liveblog.servers);
            data.servers.rest = browserUrl(data.servers.rest);
            if (data.servers.frontend) {
                data.servers.frontend = browserUrl(data.servers.frontend);
            }
            this.set(data);
        }
    });
});
