define([
	'jquery',
	'gizmo/view-events',
	'livedesk-embed/views/post',
	'utils/date-format',
	'utils/ie-polyfill',
	'livedesk-embed/dispatcher',
	'jquery/tmpl',
	'jquery/scrollspy',
	'livedesk-embed/models/blog',
	'tmpl!theme/container',
	'jquery/xdomainrequest'
], function($, Gizmo, PostView, dateFormat) {
	dateFormat.i18n = {
		dayNames: _("Sun,Mon,Tue,Wed,Thu,Fri,Sat,Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday").toString().split(","),
		monthNames: _("Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,January,February,March,April,May,June,July,August,September,October,November,December").toString().split(",")
	};
	return Gizmo.View.extend({
		limit: 6,
		hashIdentifier: 'livedeskitem=',
		location: '',
		_views: [],
		el: '#livedesk-root',
		timeInterval: 10000,
		events: {
			'#loading-more': { click: 'loadingMore' },
			'#load-more': { click: 'loadMore' }
		},
		idInterval: 0,
		flags: {},
		scroll: {
			element: null,
			start: 0
		},
		resetFlags: function(){
			this.flags = {
				addAllPending: false,
				more: false,
				loadingMore: false,
				atEnd: false
			}
		},
		autoRender: true,
		pendingAutoupdates: [],
		loadMore: function(evt) {
			var self = this;
			this.resetFlags();
			self.el.find('#liveblog-post-list').html('');
			for(i=0, count = self._views.length; i<count; i++) {
				self._views[i].rendered = false;
			}
			self._views = [];
			delete self.filters;
			var postPublished = self.model.get('PostPublished');
			postPublished._list = [];						
			postPublished.resetStats();
			postPublished
				.limit(postPublished._stats.limit)
				.offset(postPublished._stats.offset)
				.auto({ data: { thumbSize: 'medium'} });
			$(this).hide();			
		},
		showLiner: function()
		{
			var self = this;
			$('#load-more').show();
		},
		loadingMore: function(evt) {
			var self = this;
			//console.log(self.flags);
			if(self.flags.atEnd || self.flags.loadingMore)
				return;
			self.flags.loadingMore = true;
			self.flags.more = true;
			var delta = self.model.get('PostPublished').delta;
				postPublished = self.model.get('PostPublished')
			if(self.filters) {
				$.each(self.filters, function(method, args) {
					postPublished[method].apply(postPublished, args);
				});
			}
			postPublished
				.xfilter(self.xfilter)
				.limit(postPublished._stats.limit)
				.offset(postPublished._stats.offset)
				.sync({ data: { thumbSize: 'medium'} }).done(function(data){				
					var total = self.model.get('PostPublished').total;
					self.toggleMoreVisibility();
					if(self._views.length >= total) {
						self.flags.atEnd = true;
					}
					self.flags.more = false;
					self.flags.loadingMore = false;
				});
		},
		more: function(evt) {
			var self = this;
			if(self.flags.atEnd || self.flags.more)
				return;
			self.flags.more = true;
			var delta = self.model.get('PostPublished').delta;
				postPublished = self.model.get('PostPublished')
			if(self.filters) {
				$.each(self.filters, function(method, args) {
					postPublished[method].apply(postPublished, args);
				});
			}
			postPublished
				.xfilter(self.xfilter)
				.limit(postPublished._stats.limit)
				.offset(postPublished._stats.offset)
				.sync().done(function(data){				
					var total = self.model.get('PostPublished').total;
					if(self._views.length >= total) {
						self.flags.atEnd = true;
						$("#loading-more", self.el).hide();
					}
					self.flags.more = false;
				});
		},
		setIdInterval: function(fn){
			this.idInterval = setInterval(fn, this.timeInterval);
			return this;
		},
		pause: function(){
			var self = this;
			clearInterval(self.idInterval);
			return this;
		},
		sync: function(){
			var self = this;
			this.auto().pause().setIdInterval(function(){self.auto();});
		},			
		auto: function(){
			this.model.xfilter().sync({force: true});
			return this;
		},                      
		gotoHash : function() {
			if (location.hash.length > 0) {
				var topHash = location.hash;
				location.hash = '';
				location.hash = topHash;
			}
		},
		init: function()
		{
			var self = this;
			self.resetFlags();
			self._views = [];
			self.location = window.location.href.split('#')[0];
			self.rendered = false;
			if($.type(self.url) === 'string')
				self.model = new Gizmo.Register.Blog(self.url.replace('my/',''));				
			self.xfilter = 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, Author.Source.IsModifiable, IsModified, ' +
							   'AuthorImage, AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta, IsPublished, Creator.FullName, PostVerification.Status.Key, Author.Source.Type.Key';
			//self.xfilter = 'CId';								   
			self.model.on('read', function()
			{
				//console.log('read');
				if(!self.rendered) {
					var hashIndex, 
						orderhash = window.location.href.split('?'),
						postPublished = self.model.get('PostPublished');
						postPublished
							.on('read readauto', self.render, self)
							.on('addings', self.addAll, self)
							.on('addingsauto',self.addAllAutoupdate, self)
							.on('removeingsauto', self.removeAllAutoupdate, self)
							.xfilter(self.xfilter)
							.limit(postPublished._stats.limit);
					if(orderhash[1] && ( (hashIndex = orderhash[1].indexOf(self.hashIdentifier)) !== -1)) {
						var order = parseFloat(orderhash[1].substr(hashIndex+self.hashIdentifier.length));
						self.filters = {end: [order, 'order']};
						postPublished
							.one('rendered', self.showLiner, self)
							.end(order, 'order')
							.sync({ data: { thumbSize: 'medium'} });
					} else {
							postPublished
								.offset(postPublished._stats.offset)
								.auto({ data: { thumbSize: 'medium'} });
					}
				}
				self.rendered = true;
			}).on('update', function(e, data){
				self.ensureStatus();
				self.renderBlog();
			}).on('sync',function(){
				self.updateingStatus();
			})
			.on('synced', function(){
				self.updateStatus();
			});
			self.sync();				
		},
		removeOne: function(view)
		{
			var 
				self = this,
				pos = self._views.indexOf(view),
				pos2 = self.model.get('PostPublished')._list.indexOf(view.model);
			if(pos !== -1 ) {
				self.model.get('PostPublished').total--;					
				self._views.splice(pos,1);
				if(pos2 !== -1) 
					self.model.get('PostPublished')._list.splice(pos2,1);
				self.markScroll();
			}
			return self;
		},
		/*!
		 * Order given view in timeline
		 * If the view is the first one the it's added after #load-more selector
		 * returns the given view.
		 */
		orderOne: function(view) {
            var pos = this.findView(view);

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
			pos = this.findView(view);
			if( pos === 0 ){
				/*!
				 * If the view is the first one the it's added after #load-more selector.
				 *   else
				 *   Reposition the dom element before the old (postion 1) first element.
				 */
				if( this._views.length === 1) {
					this.el.find('#load-more').after(view.el);
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

        findView: function(view) {
            for (var i = 0, length = this._views.length; i < length; i++) {
                if (view.model.href === this._views[i].model.href) {
                    return i;
                }
            }

            return -1;
        },

		addOne: function(model)
		{
			var view = new PostView({model: model, _parent: this});
            model.postView = view;
			return this.orderOne(view);
		},
		toggleStatusCount: function()
		{
			if(this.pendingAutoupdates.length !== 0) {
				var n = this.pendingAutoupdates.length;
				$("#liveblog-status-count",this.el).text(ngettext('one new post', '%(count)s new posts',n ).format( { count: n})).show();
			} else {
				$("#liveblog-status-count",this.el).hide();
			}
		},
		removeAllAutoupdate: function(evt, data)
		{
			for (var i in data) {
                if ('postView' in data[i]) {
					data[i].postView.remove();
				}
			}

			this.markScroll();
		},
		addAllAutoupdate: function(evt, data)
		{
			if(this.autoRender) {
				if(data.length) {
					for(var i = 0, count = data.length; i < count; i++) {
						this.addOne(data[i]);
						this.model.get('PostPublished').total++;
					}
					this.markScroll();
				}
			} else if(data.length !== 0){
				this.pendingAutoupdates = this.pendingAutoupdates.concat(data);
				this.toggleStatusCount();
			}
		},
		addAllPending: function()
		{
			if(!this.flags.addAllPending && this.pendingAutoupdates.length) {
				this.flags.addAllPending = true;
				//console.log('addPending: ',this.pendingAutoupdates);
				//console.log(this.pendingAutoupdates.length);
				for(var i = 0, count = this.pendingAutoupdates.length; i < count; i++) {
					//console.log(i, this.pendingAutoupdates[i]);
					this.addOne(this.pendingAutoupdates[i]);
				}
				this.pendingAutoupdates = [];
				this.toggleStatusCount();
				this.markScroll();
			}
			this.flags.addAllPending = false;
		},
		addAll: function(evt, data)
		{
			var i, self = this;
			for(i = 0, count = data.length; i < count; i++) {
				this.addOne(data[i]);
			}
			this.toggleMoreVisibility();
		},
		ensureStatus: function(){
			if(this.model.get('ClosedOn')) {
				var closedOn = new Date(Date.parse(this.model.get('ClosedOn')));
				this.pause();
				this.model.get('PostPublished').stop();					
				this.el.find('#liveblog-status-time').html(_('The liveblog coverage was stopped ')+closedOn.format(_('mm/dd/yyyy HH:MM')));
			}
		}, 
		updateingStatus: function()
		{
			this.el.find('#liveblog-status-time').html(_('updating...')+'');
		},
		updateStatus: function()
		{
			var self = this,
				now = new Date();
			if(this.model.get('ClosedOn') === undefined) {
				this.el.find('#liveblog-status').fadeOut(function(){
					var t = '<time data-date="'+now.getTime()+'">'+now.format(_('HH:MM'))+"</time>";
					$(this).find('#liveblog-status-time')
						.html(_('updated at %s').format([t])).end().fadeIn();
					$.dispatcher.triggerHandler('after-render',self);
				});
			}
		},
		renderBlog: function()
		{
			$(this.el)
				.find('[gimme="blog.title"]').html(this.model.get('Title')).end()
				.find('[gimme="blog.description"]').html(this.model.get('Description'));
		},
		toggleMoreVisibility: function()
		{	
			if(this.model.get('PostPublished')._stats.offset >= this.model.get('PostPublished')._stats.total ) {
				$('#loading-more',this.el).hide();
			} else {
				$('#loading-more',this.el).show();
			}			
		},
		markScroll: function()
		{
			var self = this;
			self.scroll.element = $("#liveblog-posts :not(#load-more)", self.el).first();
			//console.log(self.scroll.element);
			self.scroll.start = self.scroll.element.offset().top;		
		},
		render: function(evt)
		{				
			var self = this,
				data,
				auxView,
				postPublished = self.model.get('PostPublished');
			self.el.tmpl('theme/container');
			self.renderBlog();
			self.ensureStatus();
			data = postPublished._list;
			postPublished.total = postPublished.listTotal;
			self.toggleMoreVisibility();
			var next = self._latest, current, model, i = data.length;                               
			self.views=[];
			self.renderedTotal = i;
			for(var i = 0, count = data.length; i < count; i++) {
				//console.log(data[i]);
				data[i].on('rendered', self.renderedOn, self);
				auxView = self.addOne(data[i]);
				self.views.push(auxView);
			}
			self.model.get('PostPublished').triggerHandler('rendered');
			$("#pintotop,#liveblog-status-count", self.el).on(self.getEvent('click'), function(evt){
				evt.preventDefault();
				$("#liveblog-posts",self.el).scrollTop(0);
			});
			self.markScroll();
			$("#liveblog-posts", self.el).scroll(function(e) {
				if ( !self.flags.atEnd && ($(this).outerHeight() + 1 >= ($(this).get(0).scrollHeight - $(this).scrollTop()))) {
					self.more();
                }

				if (self.scroll.element.offset().top < self.scroll.start) {
					self.autoRender = false;
					$("#liveblog-status", self.el).addClass("shadow")
				} else {
					self.autoRender = true;
					self.addAllPending();
					$("#liveblog-status", self.el).removeClass("shadow");
				}
			});
			$.dispatcher.triggerHandler('after-render',this);
		},
		renderedOn: function(){
		   this.renderedTotal--;
		   if(!this.renderedTotal) {
				this.closeAllButFirstWrapup();
		   }
		},
		closeAllButFirstWrapup: function(views) {
			var first = true, views= this.views;
			views.reverse();
			for (var i = 0; i < views.length; i++) {
				 if ($(views[i].el).hasClass('wrapup')) {
					  views[i]._toggleWrap($(views[i].el));
				 }
			}
		}
	});
});
