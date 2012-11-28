define([
	'jquery',
	'gizmo/superdesk',
	'livedesk-embed/views/post',	
	'jquery/tmpl',
	'jquery/scrollspy',
	'livedesk-embed/models/blog',
	'tmpl!theme/container'
], function($, Gizmo, PostView) {
	return Gizmo.View.extend({
		limit: 6,
		offset: 0,
		hashIdentifier: 'livedeskitem=',
		location: '',
		el: '#livedesk-root',
		timeInterval: 10000,
		idInterval: 0,
		_latestCId: 0,
		inProgress: false,
		atEnd: false,
		more: function(evt) {
			var self = this;
			if(self.atEnd || self.inProgress)
				return;
			self.inProgress = true;
			var delta = self.model.get('PostPublished').delta;
				postPublished = self.model.get('PostPublished')
			if(self.filters) {
				$.each(self.filters, function(method, args) {
					postPublished[method].apply(postPublished, args);
				});
			}
			postPublished
				.xfilter(self.xfilter)
				.limit(self.limit)
				.offset(self._views.length)
				.sync().done(function(data){				
					var total = self.model.get('PostPublished').total;
					if(self._views.length >= total) {
						self.atEnd = true;
						$("#liveblog-posts li#loading-more", self.el).hide();
					}
					self.inProgress = false;
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
				this.el.find('#liveblog-status').html(_('The liveblog coverage was stopped ')+closedOn.format(_('mm/dd/yyyy HH:MM:ss')));
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
							   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta';
			//self.xfilter = 'CId';								   
			self.model.on('read', function()
			{
				//console.log('read');
				if(!self.rendered) {
					var hashIndex, 
						orderhash = window.location.href.split('#'),
						postPublished = self.model.get('PostPublished')
							.on('read readauto', self.render, self)
							.on('addings addingsauto', self.addAll, self)
							.on('addingsauto', self.updateTotal, self)
							.on('updates updatesauto', self.updateStatus, self)
							.on('beforeUpdate', self.updateingStatus, self)
							.xfilter(self.xfilter)
							.limit(self.limit);
					if(orderhash[1] && ( (hashIndex = orderhash[1].indexOf(self.hashIdentifier)) !== -1)) {
						var order = parseFloat(orderhash[1].substr(hashIndex+self.hashIdentifier.length));
						self.filters = {end: [order, 'order']};
						postPublished
							.one('rendered', self.showLiner, self)
							.end(order, 'order')
							.sync();
					} else {
							postPublished
								.offset(self.offset).auto();
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
			$('#liveblog-firstmore')
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
						.limit(self.limit)
						.offset(self.offset).auto();
					$(this).hide();
				})
				.show();
		},
		removeOne: function(view)
		{
			var 
				self = this,
				pos = self._views.indexOf(view);
			//console.log(self.model.get('PostPublished').total);
			self.model.get('PostPublished').total--;					
			self._views.splice(pos,1);
			return self;
		},
		reorderOne: function(view) {
			var self = this;
			self._views.sort(function(a,b){
				return a.order - b.order;
			});
			pos = self._views.indexOf(view);
			//console.log(pos, '===',(self._views.length-1));
			if(pos === 0) {
				//console.log(view.model.get('Content'), '.insertAfter('+self._views[1].model.get('Content')+');');
				view.el.insertAfter(self._views[1].el);
			} else {
				//console.log(view.model.get('Content'), '.insertBefore('+self._views[pos>0? pos-1: 1].model.get('Content')+');');
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
		updateTotal: function(evt,data)
		{
			var i = data.length;
			while(i--) {
					this.model.get('PostPublished').total++;
			}
			//console.log('total: ',this.model.get('PostPublished').total);
		},
		addAll: function(evt, data)
		{
			var i = data.length;
			while(i--) {
				this.addOne(data[i]);
			}
			this.toggleMoreVisibility();
		},
		updateingStatus: function()
		{
			this.el.find('#liveblog-status').html(_('updating...'));
		},
		updateStatus: function()
		{
			var now = new Date();
			this.el.find('#liveblog-status').fadeOut(function(){
				$(this).text(_('updated on ')+now.format(_('HH:MM:ss'))).fadeIn();
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
			if(this.limit >= this.model.get('PostPublished').total ) {
				$('#loading-more',this.el).hide();
			} else {
				$('#loading-more',this.el).show();
			}			
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
			while(i--) {
				data[i].on('rendered', self.renderedOn, self);
				auxView = self.addOne(data[i]);
				self.views.push(auxView);
			}
			self.model.get('PostPublished').triggerHandler('rendered');
			$("#pintotop", self.el).on(self.getEvent('click'), function(){
				$("#liveblog-posts",self.el).scrollTop(0);
			});
			var element = $("#liveblog-posts li:not(#load-more)", self.el).first(),
				start = element.offset().top;
			$("#liveblog-posts", self.el).scroll(function() {
				var r   = element.offset().top;
				if( $(this).outerHeight() === ($(this).get(0).scrollHeight - $(this).scrollTop()))
					self.more();
				if (r < start) {
					$("#liveblog-status", self.el).addClass("shadow")
				}
				else {
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