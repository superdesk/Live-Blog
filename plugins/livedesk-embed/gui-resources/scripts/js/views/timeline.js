define([
	'jquery',
	'gizmo/superdesk',
	'livedesk-embed/views/post',	
	'jquery/tmpl',
	'jquery/scrollspy',
	'livedesk-embed/models/blog',
	'tmpl!theme/container',
	'jquery/xdomainrequest'
], function($, Gizmo, PostView) {
	$.support.cors = true;
	return Gizmo.View.extend({
		limit: 6,
		hashIdentifier: 'livedeskitem=',
		location: '',
		_views: [],
		el: '#livedesk-root',
		timeInterval: 10000,
		events: {
			'#loading-more': { click: 'moreButton' }
		},
		idInterval: 0,
		flags: { 
			addAllPending: false,
			more: false,
			moreButton: false,
			atEnd: false
		},
		scroll: {
			element: null,
			start: 0
		},
		autoRender: true,
		pendingAutoupdates: [],
		moreButton: function(evt) {
			var self = this;
			if(self.flags.atEnd || self.flags.moreButton)
				return;
			self.flags.moreButton = true;
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
					self.toggleMoreVisibility();
					if(self._views.length >= total) {
						self.flags.atEnd = true;
					}
					self.flags.more = false;
					self.flags.moreButton = false;
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
						$("#liveblog-posts li#loading-more", self.el).hide();
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
		ensureStatus: function(){
			if(this.model.get('ClosedOn')) {
				var closedOn = new Date(this.model.get('ClosedOn'));
				this.pause();
				this.model.get('PostPublished').pause();					
				this.el.find('#liveblog-status-time').html(_('The liveblog coverage was stopped ')+closedOn.format(_('dd.mm.yyyy, HH:MM:ss')));
			}
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
			self._views = [];
			self.location = window.location.href.split('#')[0];
			self.rendered = false;
			if($.type(self.url) === 'string')
				self.model = new Gizmo.Register.Blog(self.url.replace('my/',''));				
			self.xfilter = 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
							   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta, IsPublished, Creator.FullName';
			//self.xfilter = 'CId';								   
			self.model.on('read', function()
			{
				//console.log('read');
				if(!self.rendered) {
					var hashIndex, 
						orderhash = window.location.href.split('#'),
						postPublished = self.model.get('PostPublished');
						postPublished
							.on('read readauto', self.render, self)
							.on('addings', self.addAll, self)
							.on('addingsauto',self.addAllAutoupdate, self)
							.on('removeingsauto', self.removeAllAutoupdate, self)
							.on('updateauto', self.updateStatus, self)
							.on('beforeUpdate', self.updateingStatus, self)
							.xfilter(self.xfilter)
							.limit(postPublished._stats.limit);
					if(orderhash[1] && ( (hashIndex = orderhash[1].indexOf(self.hashIdentifier)) !== -1)) {
						var order = parseFloat(orderhash[1].substr(hashIndex+self.hashIdentifier.length));
						self.filters = {end: [order, 'order']};
						postPublished
							.one('rendered', self.showLiner, self)
							.end(order, 'order')
							.sync();
					} else {
							postPublished
								.offset(postPublished._stats.offset)
								.auto();
					}
				}
				self.rendered = true;
			}).on('update', function(e, data){
				self.ensureStatus();
				self.renderBlog();
			});
			self.sync();				
		},
		showLiner: function()
		{
			var self = this;
			$('#load-more')
				.on('click', function(){
					self.el.find('#liveblog-post-list').html('');
					for(i=0, count = self._views.length; i<count; i++) {
						self._views[i].rendered = false;
					}
					self._views = [];
					delete self.filters;
					var postPublished = self.model.get('PostPublished');
					postPublished._list = [];						
					postPublished._latestCId = 0;
					postPublished
						.limit(postPublished._stats.limit)
						.offset(postPublished._stats.offset)
						.auto();
					$(this).hide();
				})
				.show();
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
		reorderOne: function(view) {
			var self = this;
			self._views.sort(function(a,b){
				return a.order - b.order;
			});
			pos = self._views.indexOf(view);
			if(pos === 0) {
				view.el.insertAfter(self._views[1].el);
			} else {
				view.el.insertBefore(self._views[pos>0? pos-1: 1].el);
			}
		},
		addOne: function(model)
		{
			var self = this,
				current = new PostView({model: model, _parent: self}),
				count = self._views.length;
			model.postview = current;
			current.order =  parseFloat(model.get('Order'));
			if(!count) {
				this.el.find('#load-more').after(current.el);
				self._views = [current];
			} else {
				var next, prev;
				for(i=0; i<count; i++) {
					if(current.order>self._views[i].order) {
						next = self._views[i];
						nextIndex = i;
					} else if(current.order<self._views[i].order) {
						prev = self._views[i];
						prevIndex = i;
						break;
					}						
				}
				//console.log(prev && prev.order,'<<',current.order, '>>',next && next.order);
				if(prev) {
					//console.log('next');
					current.el.insertAfter(prev.el);
					self._views.splice(prevIndex, 0, current);					
				} else if(next) {
					//console.log('prev');
					current.el.insertBefore(next.el);
					self._views.splice(nextIndex+1, 0, current);
				}
			}
			return current;
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
			var self = this;
			for( var i = 0, count = data.length; i < count; i++ ) {
				if(data[i].postview) {
					data[i].postview.remove();
				}
			}
			self.markScroll();
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
		updateingStatus: function()
		{

			this.el.find('#liveblog-status-time').html(_('updating...'));
		},
		updateStatus: function()
		{
			var now = new Date();
			this.el.find('#liveblog-status').fadeOut(function(){
				
				$(this).find('#liveblog-status-time')
					.attr('time',now.format())
					.text(_('updated on %s').format(now.format(_('HH:MM:ss')))).end().fadeIn();
			});
		},
		renderBlog: function()
		{
			//$(this.el).find('article')
				//.find('h2').html(this.model.get('Title')).end()
				//.find('p').html(this.model.get('Description'));
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
			self.scroll.element = $("#liveblog-posts li:not(#load-more)", self.el).first();
			//console.log(self.scroll.element);
			self.scroll.start = self.scroll.element.offset().top;		
		},
		render: function(evt)
		{				
			var self = this,
				data,
				auxView,
				postPublished = self.model.get('PostPublished');;
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
			$("#liveblog-posts", self.el).scroll(function() {
				if( !self.flags.atEnd && ($(this).outerHeight() === ($(this).get(0).scrollHeight - $(this).scrollTop())))
					self.more();
				if (self.scroll.element.offset().top < self.scroll.start) {
					self.autoRender = false;
					$("#liveblog-status", self.el).addClass("shadow")
				}
				else {
					self.autoRender = true;
					self.addAllPending();
					$("#liveblog-status", self.el).removeClass("shadow");
				}

			});	
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