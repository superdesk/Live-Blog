'use strict';

define([
    'lodash',
    'lib/utils',
    'views/base-view',
    'lib/lodash/defaults-deep',
    'views/post-templates'
], function(_, utils, BaseView) {

    return BaseView.extend({

        // Set `el` to the top level element from the template
        // instead of the default behaviour of inserting a `div` element
        // (Backbone.LayoutManager).
        el: false,

        // `propertiesObj._cacheData` is used to cache some useful data.
        propertiesObj: {
            _cacheData: {
                itemName: false
            }
        },

        initialize: function() {
            _.defaultsDeep(this, this.propertiesObj);
            this.order = parseFloat(this.model.get('Order'));

            utils.dispatcher.trigger('initialize.post-view', this);

            this.setTemplate(this.itemName());

            this.listenTo(this.model, 'change:CId', this.update);
        },

        // If the model has changed re-render the view,
        // except if the post was reordered,
        // unpublished or deleted, in which case the
        // event will be handled by posts view.
        update: function() {
            if (!this.model.hasChanged('Order') &&
                !this.model.hasChanged('DeletedOn') &&
                !this.model.hasChanged('isPublished')) {
                this.render();
            }
        },

        // Backbone.LayoutManager `serialize`.
        serialize: function() {
            var data = this.model.toJSON();
            data.baseItem = this.themedTemplate('themeBase/item/base');
            if (this.permalink && typeof this.permalink === 'function') {
                data.permalink = this.permalink();
            }
            return data;
        },

        // To be called client side if the post has been already
        // rendered server side.
        // It manually set fields and throw events as if `render`
        // had been executed.
        alreadyRendered: function() {
            this.fakeViewRendering();
            utils.dispatcher.trigger('before-render.post-view', this);
            utils.dispatcher.trigger('after-render.post-view', this);
        },

        // Backbone.LayoutManager `beforeRender`.
        beforeRender: function() {
            utils.dispatcher.trigger('before-render.post-view', this);
        },

        // Backbone.LayoutManager `afterRender`.
        afterRender: function() {
            utils.dispatcher.trigger('after-render.post-view', this);
        },

        // Return the item name from `propertiesObj._cacheData`,
        // if it's already there. Otherwise find it out
        // and save it for the next time.
        itemName: function() {
            if (this._cacheData.itemName) {
                return this._cacheData.itemName;
            }
            var item,
                post = this.model;
            if (post.get('Author') &&
                post.get('Author').Source.IsModifiable ===  'True' ||
                post.get('Author').Source.Name === 'internal') {
                if (post.get('Type').Key === 'advertisement') {
                    item = 'item/posttype/infomercial';
                } else {
                    item = 'item/posttype/' + post.get('Type').Key;
                }
            } else if (post.get('Author').Source.Name === 'google') {
                item = 'item/source/google/' + post.get('Meta').type;
            } else {
                if (post.get('Author').Source.Name === 'advertisement') {
                    item = 'item/source/infomercial';
                } else {
                    item = 'item/source/' + post.get('Author').Source.Name;
                }
            }
            this._cacheData.itemName = 'themeBase/' + item;
            return this._cacheData.itemName;
        }
    });
});
