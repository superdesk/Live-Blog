/* jshint maxparams: 9 */
'use strict';

define([
    'backbone',
    'underscore',
    'plugins',
    'lib/utils',
    'dust'
], function(Backbone, _, plugins, utils, dust) {
    //animation effects for the wrapup
    var effects = {
        hide: 'slideUp',
        show: 'slideDown'
    };
    //check if we are client side (browser)
    if (utils.isClient){
        //once posts-view is rendered
        utils.dispatcher.once('initialize.posts-view', function(view) {
            //add the on click handler for post.wrapup
            view.clientEvents({'click [data-gimme="post.wrapup"]': 'wrapupToggle'});
            view.wrapupToggle = function(evt) {
                //make sure we get the closest post-wrapup to the actual click location
                var item = view.$(evt.target).closest('[data-gimme="post.wrapup"]');
                //get the name of the css class used for wrapup post when open
                var wrapupOpen = item.attr('data-wrapup-open');
                //do the actual toggle
                if (item.hasClass(wrapupOpen)) {
                    item.removeClass(wrapupOpen);
                    item.nextUntil('[data-gimme="post.wrapup"],[data-gimme="posts.nextPage"]')[effects.hide]();
                } else {
                    item.addClass(wrapupOpen);
                    item.nextUntil('[data-gimme="post.wrapup"],[data-gimme="posts.nextPage"]')[effects.show]();
                }
            };
        });
    }
});
