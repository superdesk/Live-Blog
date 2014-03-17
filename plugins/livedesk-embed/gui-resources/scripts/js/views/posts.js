define([
	'jquery',
	'gizmo/view-events',
	'views/post',
	'dispatcher'
], function($, Gizmo, PostViewDef) {
	return function(){
		"use strict";
		var PostView = PostViewDef(),
			PostsView = Gizmo.View.extend({
			events: {},
			_flags: {
				autoRender: true,
				addAllPending: false
			},
			_config: {
				timeInterval: 10000,
				data: {
					thumbSize: 'medium'
				},
				collection: {
					xfilter: 'PublishedOn, DeletedOn, Order, Id,' +
								   'CId, Content, CreatedOn, Type, '+
								   'AuthorName, Author.Source.Name, Author.Source.Id, Author.Source.IsModifiable,' +
								   'IsModified, AuthorImage,' +
								   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id,' +
								   'Meta, IsPublished, Creator.FullName, Author.Source.Type.Key'
				}
			},
			pendingAutoupdates: [],
			init: function() {
				var self = this;
				self._views = [];
				$.each(self._config.collection, function(key, value) {
					if($.isArray(value))
						self.collection[key].apply(self.collection, value);
					else
						self.collection[key](value);
				});
				self.collection
					.on('read readauto', self.render, self)
					.on('addings', self.addAll, self)
					.on('addingsauto',self.addingsAuto, self)
					.on('removeingsauto', self.removeAllAutoupdate, self)
					.auto()
					.autosync({ data: self._config.data, preprocessTime: 250 });
			},
			removeOne: function(view) {
				var 
					self = this,
					pos = self._views.indexOf(view),
					pos2 = self.collection._list.indexOf(view.model);
				if(pos !== -1 ) {
					self.collection._stats.total--;					
					self._views.splice(pos,1);
					if(pos2 !== -1) 
						self.collection._list.splice(pos2,1);
				}
				self.triggerHandler('remove',[view.model]);
				return self;
			},

			addOne: function(model) {
				var view = new PostView({model: model, _parent: this});
	            model.postView = view;
				return this.orderOne(view);
			},

			/*!
			 * Order given view in timeline
			 * If the view is the first one the it's added after #load-more selector
			 * returns the given view.
			 */
			orderOne: function(view) {
				var pos = this._views.indexOf(view);
				/*!
				 * View property order need to be set here
				 *   because could be multiple updates and 
				 *   orderOne only works for one update.
				 */
				view.order = parseFloat(view.model.get('Order'));
				/*!
				 * If the view isn't in the _views vector
				 *   add it.
				 */
				if ( pos === -1 ) {
					this._views.push(view);
				}
				/*!
				 * Sort the _view vector descendent by view property order.
				 */
				this._views.sort(function(a,b){
					return b.order - a.order;
				});
				/*!
				 * Search it again in find the new position.
				 */
				pos = this._views.indexOf(view);
				if( pos === 0 ){
					/*!
					 * If the view is the first one the it's added after #load-more selector.
					 *   else
					 *   Reposition the dom element before the old (postion 1) first element.
					 */
					if( this._views.length === 1) {
						if(this.el.children().length){
							var before = $('[data-gimme="posts.beforePage"]:last',this.el),
								after = $('[data-gimme="posts.afterPage"]:first',this.el)
							if(before.length)
								before.after(view.el);
							else if (after.length)
								after.before(view.el);
							else
								this.el.prepend(view.el)
						} else {
							this.el.append(view.el);	
						}
					} else {
						view.el.insertBefore(this._views[1].el);
					}
				} else {
					/*!
					 * Reposition the dom element after the previous element.
					 */
					view.el.insertAfter(this._views[pos-1].el);
				}
				return view;
			},

			addingsAuto: function(evt, data) {
				var self = this;
				if(data.length) {
					self.pendingAutoupdates = self.pendingAutoupdates.concat(data);
				}
				self.addAllAutoupdate(evt);
			},
			addAllPending: function(evt) {
				var self = this;
				if(!self._flags.addAllPending && self.pendingAutoupdates.length) {
					self._flags.addAllPending = true;
					self._parent.hideNewPosts();
					for(var i = 0, count = this.pendingAutoupdates.length; i < count; i++) {
						this.addOne(this.pendingAutoupdates[i]);
					}
					$.dispatcher.triggerHandler('added-pending.posts-view',self);
	            	self.triggerHandler('addingsauto',[self.pendingAutoupdates]);
					self.pendingAutoupdates = [];
				}
				self._flags.addAllPending = false;
			},

			addAllAutoupdate: function(evt) {
				var self = this;
				if(self._flags.autoRender) {
					self.addAllPending(evt);
					$.dispatcher.triggerHandler('added-auto.posts-view',self);
				} else {
					self._parent.showNewPosts(self.pendingAutoupdates.length);
				}
			},

			addAll: function(evt, data) {
				var self = this;
				self.triggerHandler('addings',[data]);
				for(var i = 0, count = data.length; i < count; i++) {
					this.addOne(data[i]);
				}
				if(data.length)
					$.dispatcher.triggerHandler('add-all.posts-view',self);
			},

			render: function(evt, data) {		
				var self = this;
				self.collection.triggerHandler('rendered');
				self.addAll(evt, data);
				$.dispatcher.triggerHandler('rendered-after.posts-view',self);
			}
		});
		$.dispatcher.triggerHandler('class.posts-view',PostsView);
		return PostsView;
	}
});
