'use strict';
require.config({
    paths: {
        'twitterWidgets': '//platform.twitter.com/widgets'
    },
    shim: {
        'twitterWidgets': {
            'exports': 'twttr'
        }
    }
});

define([
    'underscore',
    'backbone',
    'plugins',
    'dust',
    'lib/utils'
], function (_, Backbone, plugins, dust, utils) {
    plugins['twitter-widgets'] = function (config) {
        if (utils.isClient) {
            utils.dispatcher.on('before-render.post-view', function (view) {
                if (view.model.get('item') !== 'source/twitter') {
                    return;
                }
                if (!view.parentView()._twitterPosts) {
                    view.parentView()._twitterPosts = [];
                }
                view.parentView()._twitterPosts.push(view);
            });

            //still a problem with this event
            utils.dispatcher.on('add-all.posts-view', function (view) {
                addWaypoints(view);
            });

            var addWaypoints = function (self) {
                if (!self._twitterPosts) {
                    return;
                }

                require(['twitterWidgets', 'waypoints'], function (twttr) {
                    twttr.ready(function () {
                        _.each(self._twitterPosts, function (post, index, tweetList) {
                            post.$el.waypoint(function () {
                                var id_str = post.model.get('Meta').id_str;
                                twttr.widgets.createTweet(
                                    id_str,
                                    post.$el.find('.post-content-full').get(0),
                                    function () {
                                        post.$el.find('.post-core-content').remove();
                                    }, {
                                        cards: 'all'
                                    }
                                );
                            }, {
                                triggerOnce: true,
                                offset: '120%',
                                context: self.el
                            });
                        });
                        self._twitterPosts = [];
                    });
                }, function (err) {
                    // twitterWidgets dependency failed to load, probably blocked by user with adblock
                    return;
                });
            };
        }
    };
    return plugins['twitter-widgets'];
});
