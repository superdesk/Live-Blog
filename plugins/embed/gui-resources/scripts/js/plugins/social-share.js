/* jshint maxparams: 9 */
'use strict';

define([
    'backbone',
    'underscore',
    'plugins',
    'lib/utils',
    'dust',
    'lib/gettext',
    'lib/helpers/fixed-encodeURIComponent',
    'lib/helpers/visibility-toggle',
    'config/social-share-plugin',
    'tmpl!themeBase/plugins/social-share-anchor',
    'tmpl!themeBase/plugins/social-share'
], function(Backbone, _, plugins, utils, dust, gt,
    fixedEncodeURIComp, visibilityToggle, shareConf) {

    // Social share plugin only works on client
    if (utils.isClient){

        plugins['social-share'] = function(config) {

            utils.dispatcher.on('after-render.post-view', function(view) {
                // Add social share link to the view
                dust.renderThemed('themeBase/plugins/social-share-anchor', {},
                    function(err, out) {
                        view.$('[data-gimme="post.social-share-placeholder"]').html(out);
                    });
            });

            // On post view initialization
            utils.dispatcher.on('initialize.post-view', function(view) {

                // Add event to call 'share' method when share link clicked
                view.clientEvents({'click [data-gimme="post.social"]': 'share'});

                // Render the social share box containing buttons to share
                // the post in different social networks
                view.share = function(e) {
                    e.preventDefault();
                    e.stopPropagation();

                    var self = this,
                        item = self.$(e.target),
                        initialized = item.data('initialized'),
                        urlParams;

                    if (!initialized) {
                        urlParams = socialUrlParams(self);

                        // Store the share urls for the different social networks
                        self.socialShareUrls = socialUrls(urlParams);

                        // Add the box after the social share link
                        dust.renderThemed('themeBase/plugins/social-share',
                            socialParams(urlParams),
                            function(err, out) {
                                self.$('[data-gimme="post.social-share-placeholder"]').append(out);
                            });

                        // Bind events for social network buttons
                        bindShareButtonsEvents(self);

                        item.data('initialized', 1);
                    }

                    // Toggle visibility of social share box,
                    // if the box is hidden, hide other share plugins markup too
                    var socialShareBox = self.$('[data-gimme="post.share-social"]');
                    var postShare = self.$('[data-gimme^="post.share"]');
                    if (socialShareBox.css('visibility') === 'hidden') {
                        visibilityToggle(postShare, false);
                    }
                    visibilityToggle(socialShareBox);
                };

                //Open a new window for sharing the post in the desired social network
                view.openShareWindow = function(e) {
                    e.preventDefault();

                    var socialNetwork = this.$(e.target).data('gimme'),
                        height        = shareConf.shareWindowSize[socialNetwork].h,
                        width         = shareConf.shareWindowSize[socialNetwork].w,
                        shareUrl      = this.socialShareUrls[socialNetwork];

                    var options = 'resizable, height=' + height + ', width=' + width;
                    var socialShareWindow = window.open(shareUrl, '', options);
                    socialShareWindow.focus();
                    return false;
                };
            });

            // Return the parameters to construct the social sharing urls
            var socialUrlParams = function(view) {
                var blog      = view.parentView().parentView().model,
                    blogTitle = fixedEncodeURIComp(blog.get('Title')),
                    summary   = fixedEncodeURIComp(
                                view.$('.result-content .result-text:last').text());

                var permLink  = '';
                if (view.permalink && typeof view.permalink === 'function') {
                    permLink  = fixedEncodeURIComp(view.permalink());
                }

                var imgsrc    = view.$('.result-content img:first').attr('src');
                if (!imgsrc) {
                    imgsrc = Backbone.$('img:first').attr('src');
                }

                var fbURLImageComp = '';
                view.$('.result-content img').each(function(index) {
                    fbURLImageComp += gt.sprintf(shareConf.fbURLImageComp,
                                        [index, Backbone.$(this).attr('src')]);
                });

                var urlParams = {
                    pin:   [permLink, imgsrc, blogTitle],
                    twt:   [gt.gettext('Now reading'), blogTitle, permLink],
                    lin:   [permLink, blogTitle, summary],
                    ggl:   [permLink],
                    email: [gt.gettext('Check out this Live Blog'), permLink],
                    fb:    [blogTitle, summary, permLink, fbURLImageComp]
                };

                return urlParams;
            };

            // Return the sharing urls for the different social networks
            var socialUrls = function(urlParams) {
                var urls = {};

                delete urlParams.email;

                _.each(urlParams, function(value, key) {
                    urls[key] = gt.sprintf(shareConf.urls[key],
                                            urlParams[key]);
                });

                return urls;
            };

            // Return the parameters for the social sharing template
            var socialParams = function(urlParams) {
                var params = {};

                params.emailurl =  gt.sprintf(shareConf.urls.email, urlParams.email);

                return params;
            };

            // Add click events for all social network buttons
            var bindShareButtonsEvents = function(view) {
                var events = {};

                _.each(view.socialShareUrls, function(value, key) {
                    events['click [data-gimme="' + key + '"]'] = 'openShareWindow';
                });

                view.clientEvents(events);
                view.delegateEvents();
            };
        };
    }
});
