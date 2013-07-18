define([
	'jquery',
	'gizmo/view-events',
	'views/post'
], function($, Gizmo, PostView) {
	return Gizmo.View.extend({
		init: function() {
			var self = this;
			self._views = [];
			self._timeInterval = 10000;
			self._pendingAutoupdates = [];
			self.xfilter = 'PublishedOn, DeletedOn, Order, Id,' +
						   'CId, Content, CreatedOn, Type, '+
						   'AuthorName, Author.Source.Name, Author.Source.Id, Author.Source.IsModifiable,' +
						   'IsModified, AuthorImage,' +
						   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id,' +
						   'Meta, IsPublished, Creator.FullName';
			self.collection
				.on('read readauto', self.render, self)
				//.on('addings', self.addAll, self)
				//.on('addingsauto',self.addAllAutoupdate, self)
				.xfilter(self.xfilter)
				//.auto()
				.autosync();
//			this.render();
		},
		
		removeOne: function(view) {
			var 
				self = this,
				pos = self._views.indexOf(view),
				pos2 = self.collection._list.indexOf(view.model);
			if(pos !== -1 ) {
				self.collection.total--;					
				self._views.splice(pos,1);
				if(pos2 !== -1) 
					self.collection._list.splice(pos2,1);
			}
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
					this.el.append(view.el);
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

		removeAllAutoupdate: function(evt, data) {
			for (var i in data) {
                if ('postView' in data[i]) {
					data[i].postView.remove();
				}
			}

			this.markScroll();
		},

		addAllAutoupdate: function(evt, data) {
			// if(this.autoRender) {
			// 	if(data.length) {
			// 		for(var i = 0, count = data.length; i < count; i++) {
			// 			this.addOne(data[i]);
			// 			this.model.get('PostPublished').total++;
			// 		}
			// 		this.markScroll();
			// 	}
			// } else if(data.length !== 0){
			// 	this.pendingAutoupdates = this.pendingAutoupdates.concat(data);
			// 	this.toggleStatusCount();
			// }
		},

		addAll: function(evt, data) {
			var i, self = this;
			for(i = 0, count = data.length; i < count; i++) {
				this.addOne(data[i]);
			}
		},

		render: function(evt, data) {				
			var self = this;
			self.addAll(evt, data);
		}
	});
});
