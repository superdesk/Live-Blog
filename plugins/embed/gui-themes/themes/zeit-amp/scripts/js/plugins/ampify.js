define([
    'plugins',
    'lib/utils',
    'dust'
], function(plugins, utils, dust) {
    'use strict';

    plugins['ampify'] = function(config) {

        utils.dispatcher.on('after-render.post-view', function(view) {
            view.$( '*[style]' ).removeAttr( 'style' );

            switch ( view.el.className ) {
                case 'image':
                    view.$( '.post-external-image img' ).each( function() {
                        var self = this,
                            img = new Image();
                        img.src = this.src;
                        img.onload = function() {
                            view.$( self ).replaceWith( '<amp-img src="' + this.src + '" width="' + this.width + '" height="' + this.height + '" layout="responsive"></amp-img>' );
                            view.$( img ).remove();
                        };
                        view.$el.append( img );
                    });
                    break;

                case 'link':
                    view.$( '.link-thumbnail img' ).replaceWith( function() {
                        return '<amp-img src="' + this.src + '" width="' + this.width + '" height="' + this.height + '" layout="responsive"></amp-img>';
                    });
                    view.$( '.source-icon img' ).replaceWith( function() {
                        return '<amp-img src="' + this.src + '" width="16" height="16" layout="fixed"></amp-img>';
                    });
                    break;
            }

        });
    };
});
