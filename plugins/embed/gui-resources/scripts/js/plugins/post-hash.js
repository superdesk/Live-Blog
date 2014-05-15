'use strict';

define([
    'plugins',
    'lib/utils'
], function(plugins, utils) {

    plugins['post-hash'] = function(config) {

        var href,
            hash = 'liveblog[item][id]',
            hashMark = '?';

        if (utils.isClient) {
            href = window.location.href;
        } else {
            // locationHref is the host embedding the live blog
            //  (equivalent to window.location.href in the browser)
            // if none is provided just use a relative path for permanent links
            href = liveblog.locationHref || '/';
        }

        utils.dispatcher.on('initialize.post-view', function(view) {
            view.permalink = function(options) {
                var _hashMark = (options && options.hashMark) ? options.hashMark : hashMark,
                    permalink = false,
                    newHash = hash + '=' + parseFloat(view.model.get('Order'));

                if (href.indexOf(_hashMark) === -1) {
                    permalink = href + _hashMark + newHash;
                } else if (href.indexOf(hash + '=') !== -1) {
                    var regexHash = new RegExp(hash + '=[^&]*');
                    permalink = href.replace(regexHash, newHash);
                } else {
                    permalink = href + '&' + newHash;
                }
                return permalink;
            };
        });

        utils.dispatcher.on('initialize.posts-view', function(view) {
            // Find if the liveblog was accessed with a hash identifier
            //   then use it as a parameter on the collection for the first request.
            var hashIndex = href.indexOf(hash + '=');
            if (hashIndex !== -1) {
                // order.end: id of the last post loaded
                // To be passed as a param in the request for pagination
                // ex: in a blog with posts 1 2 3 4 5 6 7
                // http://localhost:8080/resources/LiveDesk/Blog/1/Post/
                //      Published?order.end=3&limit=2&offset=0
                // -> gives back posts 4 5
                // http://localhost:8080/resources/LiveDesk/Blog/1/Post/
                //      Published?order.end=3&limit=2&offset=2
                // -> gives back posts 6 7
                view.collection.syncParams.pagination['order.end'] = parseFloat(href.substr(hashIndex + hash.length + 1));

                view.flags.hasTopPage = true;

                view.flags.autoRender = false;
            }
        });
    };
});
