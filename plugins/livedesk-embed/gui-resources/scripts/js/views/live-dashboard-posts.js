define([
	'jquery',
	'gizmo/view-events',
	'views/post',
	'dispatcher'
], function($, Gizmo, PostViewDef) {
	return function(){
		var PostView = PostViewDef(),
			PostsView = Gizmo.View.extend({
			events: {},
			_flags: {
        autoRender: true
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
								   'Meta, IsPublished, Creator.FullName'
				}
			},
			pendingAutoupdates: [],

      // List of domains that display a big image in tweet card
      ImageTweetsUrlDomains: [
        "flic.kr",
        "twitpic.com"
      ],

      isPostTextLike: function(model){
        var type = model.get('Type').Key;
        if(model.isExternalSource()){
          var autor = model.get('AuthorName');
          var meta = $.parseJSON(model.get('Meta'));
          switch (autor) {
            case 'google':
              if (meta.GsearchResultClass !== 'GimageSearch'){
                return true;
              }
              break;
            case 'twitter':
              var picture = meta.entities.media;
              if (!picture){
                var urls = meta.entities.urls;
                for (i = 0; i < urls.length; i ++){
                  var url = urls[i].expanded_url;
                  for (j = 0; j < this.ImageTweetsUrlDomains.length; j++){
                    if (url && url.indexOf(this.ImageTweetsUrlDomains[j]) != -1){
                      picture = true;
                    }
                  }
                }
              }
              if (!picture){
                return true;
              }
              break;
            case 'facebook':
            case 'sms':
              return true;
              break;
          }
        } else {
          if (type === 'normal' &&
              model.get('Content').indexOf('<img src="') !== 0){
            return true;
          }
          else if (type === 'quote' || type === 'link' || type === 'wrapup'){
            return true;
          }
        }
        return false;
      },

			init: function() {
				var self = this;
        self._views = {
          fullSize: [],
          text:     []
        }
        self._viewsUpdatedFlags = {
          fullSize: false,
          text: false
        };
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
					.auto()
					.autosync({ data: self._config.data });
			},
      removeOne: function(view) {
        var
          self = this,
          pos = self._views[view.type].indexOf(view),
          pos2 = self.collection._list.indexOf(view.model);
        if(pos !== -1 ) {
          self.collection._stats.total--;
          self._views[view.type].splice(pos,1);
          if(pos2 !== -1)
            self.collection._list.splice(pos2,1);
        }
        self.triggerHandler('remove',[view.model]);
        return self;
      },

			addOne: function(model) {
				var view = new PostView({model: model, _parent: this});
        model.postView = view;
        view.type = this.isPostTextLike(model) ? 'text' : 'fullSize';
				return this.orderOne(view);
			},

			/*!
			 * Order given view in timeline
			 * returns the given view.
			 */
      orderOne: function(view) {
				var pos = this._views[view.type].indexOf(view);
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
					this._views[view.type].push(view);
				}
				/*!
				 * Sort the _view vector ascendent by view property order.
				 */
				this._views[view.type].sort(function(a,b){
					return a.order - b.order;
				});
				/*!
				 * Search it again and find the new position.
				 */
				pos = this._views[view.type].indexOf(view);
				if( pos === 0 ){
          var selector = '[data-gimme="' + view.type + '.posts.slider"]';
          this.el.children(selector).prepend(view.el);
          this._viewsUpdatedFlags[view.type] = true;
        } else {
          view.el.insertAfter(this._views[view.type][pos - 1].el)
          this._viewsUpdatedFlags[view.type] = true;
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
        if(self.pendingAutoupdates.length){
					for(var i = 0, count = this.pendingAutoupdates.length; i < count; i++) {
						this.addOne(this.pendingAutoupdates[i]);
					}
					$.dispatcher.triggerHandler('posts-view.added-pending',self);
          self.triggerHandler('addingsauto',[self.pendingAutoupdates]);
					self.pendingAutoupdates = [];
				}
			},

			addAllAutoupdate: function(evt) {
				var self = this;
				if(self._flags.autoRender) {
					self.addAllPending(evt);
          $.dispatcher.triggerHandler('posts-view.added-auto',self);
          for (var sliderType in self._viewsUpdatedFlags){
            if (self._viewsUpdatedFlags[sliderType]){
              $.dispatcher.triggerHandler('posts-view.added-auto-' + sliderType, self);
              self._viewsUpdatedFlags[sliderType] = false;
            }
          }
        }
			},

			addAll: function(evt, data) {
				var i, self = this;
				self.triggerHandler('addings',[data]);
				for(i = 0, count = data.length; i < count; i++) {
					this.addOne(data[i]);
				}
				if(data.length)
					$.dispatcher.triggerHandler('posts-view.addAll',self);
			},

			render: function(evt, data) {
				var self = this;
				self.collection.triggerHandler('rendered');
				self.addAll(evt, data);
        for (sliderType in self._viewsUpdatedFlags){
          self._viewsUpdatedFlags[sliderType] = false;
        }
				$.dispatcher.triggerHandler('posts-view.rendered',self);
			}
		});
		$.dispatcher.triggerHandler('posts-view.class',PostsView);
		return PostsView;
	}
});
