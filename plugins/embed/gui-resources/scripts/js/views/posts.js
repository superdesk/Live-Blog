'use strict';

define([
    'underscore',
    'lib/utils',
    'views/base-view',
    'views/post',
    'tmpl!themeBase/posts-list'
], function(_, utils, BaseView, PostView) {

    return BaseView.extend({

        // Set `el` to the top level element from the template
        // instead of the default behaviour of inserting a `div` element
        // (Backbone.LayoutManager).
        el: false,

        // The selector of the view root element.
        rootSel: '[data-gimme="posts.list"]',

        // Data attribute that identifies post view elements.
        postRootDataAttr: 'data-gimme-postid',

        // Return the selector of a certain post view root element.
        postRootSel: function(postId) {
            if (postId) {
                return '[' + this.postRootDataAttr + '="' + postId + '"]';
            } else {
                return '[' + this.postRootDataAttr + ']';
            }
        },

        flags: {
            // If `autoRender` is false, new posts won't be displayed
            // automatically. Used by the `pending-messages` plugin.
            autoRender: true
        },

        // Keep track of the number of "pending" (i.e. not yet displayed,
        // when `autoRender: false`) posts.
        pendingCounter: 0,

        initialize: function() {
            utils.dispatcher.trigger('initialize.posts-view', this);

            _.bindAll(this, 'insertPostView', 'orderViews', '_postViewIndex',
                            '_insertPostViewAt', '_insertPostViewAtFirstPos');

            this.setTemplate('themeBase/posts-list');

            if (utils.isClient) {
                this.listenTo(this.collection, 'reset', this.setViewOnReset);
                this.listenTo(this.collection, 'add', this.checkPending);
                this.listenTo(this.collection, 'remove', this.removePost);
                this.listenTo(this.collection, 'change:Order', this.reorderPost);
                this.listenTo(this.collection, 'change:DeletedOn', this.removePostFromCollection);
                this.listenTo(this.collection, 'change:IsPublished', this.removePostFromCollection);
            }

            this.collection.fetchPage({reset: true});
        },

        // Backbone.LayoutManager `beforeRender`.
        beforeRender: function(manage) {
            this.collection.forEach(this.insertPostView, this);
        },

        // Backbone.LayoutManager `afterRender`.
        afterRender: function() {
            utils.dispatcher.trigger('after-render.posts-view', this);
        },

        // Render the view when the collection is resetted.
        // Don't re-render posts that are already there, in case of
        // server-side HTML rendering.
        setViewOnReset: function() {
            this.fakeViewRendering();
            var postEls = this.$el.children(this.postRootSel());

            // If there are no server side rendered posts, render whole view.
            if (postEls.length === 0) {
                this.render();
                return;
            }

            // Otherwise construct nested views from DOM.
            var self = this;
            postEls.each(function(index, pEl) {
                var postEl  = self.$(pEl),
                    postId  = postEl.attr(self.postRootDataAttr),
                    postCId = postEl.data('gimme-cid').toString(),
                    post    = self.collection.get(postId),
                    postView;

                // If the post is still in the collection and hasn't changed
                // construct the postView and add it to nested views.
                if (post && postCId === post.get('CId')) {
                    postView = self.insertPostView(post, {el: self.postRootSel(postId)});
                    // Fire events for the plugins if it was already rendered.
                    postView.alreadyRendered();
                } else {
                    // Else remove markup.
                    postEl.remove();
                }
            });
            // Add new posts or posts that were removed because they had changed.
            this.collection.forEach(this.addPostIfMissing, this);

            utils.dispatcher.trigger('add-all.posts-view', this);
        },

        // Render the `post` if it's not already there.
        addPostIfMissing: function(post) {
            var i = this._postViewIndex(post.id);
            if (i === -1) {
                this.addPost(post);
            }
        },

        removePostFromCollection: function(post) {
            if (!_.isUndefined(post.get('DeletedOn')) ||
                post.get('isPublished') === 'False') {
                this.collection.remove(post);
                return true;
            }
            return false;
        },

        // Render all pending posts (when `flags.autoRender: false`).
        renderPending: function() {
            var self = this;
            this.collection.each(function(item) {
                if (item.get('pending')) {
                    self.addPost(item);
                    item.set('pending', false);
                    self.pendingCounter --;
                }
            });
            utils.dispatcher.trigger('rendered-pending.posts-view', this);
            utils.dispatcher.trigger('update-pending.posts-view', this);
        },

        // Render `post` if `flag.autoRender: true` or if loading the next page,
        // otherwise add it as a pending post.
        checkPending: function(post) {
            // `post.get('updateItem')` returns false for next page loading.
            if (!this.flags.autoRender && post.get('updateItem')) {
                post.set('pending', true);
                this.pendingCounter ++;
                utils.dispatcher.trigger('update-pending.posts-view', this);
            } else {
                this.addPost(post);
            }
        },

        // Add (render) `post` to the posts list in the correct position.
        // If the post is removed don't add it.
        addPost: function(post) {
            if (this.removePostFromCollection(post)) {
                return;
            }
            var postView = this.insertPostView(post);
            this.orderViews();
            postView.render();

            utils.dispatcher.trigger('add-all.posts-view', this);
        },

        // Remove `post` from the posts list, if it has already been rendered
        // or from the list of pending posts otherwise.
        removePost: function(post) {
            var self = this;
            var pending = post.get('pending');
            if (pending) {
                this.pendingCounter --;
                utils.dispatcher.trigger('update-pending.posts-view', this);
            } else {
                this.removeView(function(nestedView) {
                    if (nestedView.$el.is(self.postRootSel(post.id))) {
                        return nestedView;
                    }
                });
            }
        },

        // Update DOM for posts list if the posts order has changed.
        reorderPost: function(post, newOrder) {
            // If some attribute other than Order (and CId) has changed
            // remove the view and render it again in the right position.
            if (!this.onlyOrderHasChanged(post)) {
                this.removePost(post);
                this.addPost(post);
            } else {
                // Update order attribute in view.
                this.views[''][this._postViewIndex(post.id)].order =
                                                            parseFloat(newOrder);

                // Reorder views array.
                this.orderViews();

                // Detach view and insert it in new position.
                var newIndex = this._postViewIndex(post.id),
                    postEl = this.$(this.postRootSel(post.id)).detach();

                this._insertPostViewAt(this.$el, postEl, newIndex);
            }
        },

        // Backbone.LayoutManager `insert`.
        insert: function($root, $el) {
            // On 'reset' append all elements to the root element.
            if ($root.is(':empty')) {
                $root.append($el);
                utils.dispatcher.trigger('add-all.posts-view', this);
            } else {
            // On 'add' insert the new post in the right position.
                var i = this._postViewIndex($el.attr(this.postRootDataAttr));
                this._insertPostViewAt($root, $el, i);
            }
        },

        // Create a new post view and insert it at the end of the views array.
        insertPostView: function(post, options) {
            var opts = _.extend({model: post}, options);
            var postView = new PostView(opts);
            this.insertView('', postView);
            return postView;
        },

        // Order the views array according to order param in views.
        orderViews: function() {
            this.views[''] = _.sortBy(this.views[''], 'order').reverse();
        },

        // Return if `order` has been the only attribute to change
        // on post update.
        onlyOrderHasChanged: function(post) {
            return (_.size(post.changedAttributes()) > 2 &&
                post.hasChanged('CId') && post.hasChanged('Order'));
        },

        // Return the view for the first post in the list.
        firstPost: function(post) {
            return this.views[''][0];
        },

        // Return the index of the post view on the views array or -1
        // if the view is not in it.
        _postViewIndex: function(postId) {
            if (!this.views['']) {
                return -1;
            }

            var orderedIds = _.map(this.views[''], function(v) { return v.model.id; });
            return _.indexOf(orderedIds, postId);
        },

        // Insert post element in the parent list element at a given index.
        _insertPostViewAt: function($parent, $el, i) {
            if (i === 0) {
                this._insertPostViewAtFirstPos($parent, $el);
            } else if (i > 0) {
                // For adding it to a position different that the first, find
                // prev post and add it after it.
                var prevId = this.views[''][i - 1].model.id;
                $parent.children(this.postRootSel(prevId)).after($el);
            }
        },

        // Insert post element in the parent list element at first position.
        _insertPostViewAtFirstPos: function($parent, $el) {
            // Find the first post element and add it before it.
            var nextEl = $parent.children(this.postRootSel()).first();
            if (nextEl.length !== 0) {
                nextEl.before($el);
            } else {
                // If there is no first post search for pagination elements
                // and add it between them.
                var pagEl = $parent.children('[data-gimme="posts.beforePage"]');
                if (pagEl.length !== 0) {
                    pagEl.after($el);
                } else {
                    // If there is no pagination element either, append to `$parent`.
                    $parent.append($el);
                }
            }
        }
    });
});
