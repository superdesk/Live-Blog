function isOnly(data,key) {
	var count = 0;
	for(i in data) {
		count++;
		if(count>1) return false;
	};
	return (data !== undefined) && (data[key] !== undefined) && (count == 1);
}
window.livedesk.init = function() {
		var self = this,
			contentPath = self.contentPath === undefined? '': self.contentPath;		
		if (typeof jQuery == 'undefined') {
			self.loadScript('http://code.jquery.com/jquery-1.7.2.min.js', function(){
				if (typeof $.gizmo == 'undefined') {
					self.loadScript(contentPath+'gizmo.js', function(){
						self.startLoading();
					})
				}
			})
		} else {
			if (typeof $.gizmo == 'undefined') {			
				self.loadScript(contentPath+'gizmo.js', function(){
					self.startLoading();
				})
			} else {
				self.startLoading();
			}
		}
	};
	
window.livedesk.loadScript = function (src, callback) {
		var script = document.createElement("script")
		script.type = "text/javascript";
		if (script.readyState) { //IE
			script.onreadystatechange = function () {
				if (script.readyState == "loaded" || script.readyState == "complete") {
					script.onreadystatechange = null;
					callback();
				}
			};
		} else { //Others
			script.onload = function () {
				callback();
			};
		}
		script.src = src;
		document.getElementsByTagName("head")[0].appendChild(script);
	};
window.livedesk.startLoading = function() {
		var 
		User = $.gizmo.Model.extend({}),
/*		PostType = $.gizmo.Model.extend({}),
		AuthorPerson = $.gizmo.Model.extend({}),
		PostBlog = $.gizmo.Model.extend({}),
		Author = $.gizmo.Model.extend({}),
*/		
		Post = $.gizmo.Model.extend
		({
			defaults:
			{
				Creator: User
			},
			services: {
				'flickr': true,
				'google': true,
				'twitter': true,
				'facebook': true,
				'youtube': true
			},
			/**
			* Get css class based on type
			*
			* @return {string}
			*/
			getClass: function() {
				switch (this.get('Type').Key) {
					case 'wrapup':
						return 'wrapup';
						break;

					case 'quote':
						return 'quotation';
						break;

					case 'advertisement':
						return 'advertisement';
						break;

					default:
						if (this.isService()) {
							return 'service';
						}

						return 'tw';
				}
			},
			/**
			* Test if post is from service
			*
			* @return {bool}
			*/
			isService: function() {
				return this.get('AuthorName') in this.services;
			},

			/**
			* Test if post is quote
			*
			* @return {bool}
			*/
			isQuote: function() {
				return this.getClass() == 'quotation';
			},
			twitter: {
				link: {
					anchor: function(str) 
					{
						return str.replace(/[A-Za-z]+:\/\/[A-Za-z0-9-_]+\.[A-Za-z0-9-_:%&\?\/.=]+/g, function(m) 
						{
							m = m.link(m);
							m = m.replace('href="','target="_blank" href="');
							return m;
						});
					},
					user: function(str) 
					{
						return str.replace(/[@]+[A-Za-z0-9-_]+/g, function(us) 
						{
							var username = us.replace("@","");
				
							us = us.link("http://twitter.com/"+username);
							us = us.replace('href="','target="_blank" onclick="loadProfile(\''+username+'\');return(false);"  href="');
							return us;
						});
					},
					tag: function(str) 
					{
						return str.replace(/[#]+[A-Za-z0-9-_]+/g, function(t) 
						{
							var tag = t.replace(" #"," %23");
							t = t.link("http://summize.com/search?q="+tag);
							t = t.replace('href="','target="_blank" href="');
							return t;
						});
					},
					all: function(str)
					{
						str = this.anchor(str);
						str = this.user(str);
						str = this.tag(str);
						return str;
					}
				}
			}
		}),
		AutoCollection = $.gizmo.Collection.extend({
			timeInterval: 10000,
			idInterval: 0,
			_latestCId: 0,
			setIdInterval: function(fn){
				this.idInterval = setInterval(fn, this.timeInterval);
				return this;
			},
			getMaximumCid: function(data){
				for(i=0, count=data.list.length; i<count; i++) {
					var CId = parseInt(data.list[i].get('CId'))
					if( !isNaN(CId) && (this._latestCId < CId) )
						this._latestCId = CId;
				}
			},
			auto: function(){                                
				var self = this, requestOptions = {data: {'cId.since': this._latestCId}, headers: {'X-Filter': 'CId'}};
				if(this._latestCId === 0) delete requestOptions.data;
				this.triggerHandler('beforeUpdate');
				$.gizmo.Collection.prototype.sync.call(this,requestOptions).done(function(data){
					self.getMaximumCid(self.parse(data));
				});
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
			}
		});
        Posts = AutoCollection.extend({
            model: Post
        }),
       
        Blog = $.gizmo.Model.extend
        ({
            defaults: 
            {
                //Post: Posts,
                PostPublished: Posts
                //PostUnpublished: Posts
            }
        });
        
        var i=0,
        PostItemView = $.gizmo.View.extend
        ({
            init: function()
            {
				var self = this;
				self.model
					.on('read', self.render, self)
					.on('update', function(evt, data){
						if(isOnly(data, 'CId')) {
							self.model.sync(); //.xfilter(self.xfilter)
						}
						else
							self.render(evt, data);
					})
					.on('delete', self.remove, self)
					.sync();
			},
			remove: function()
			{
				var self = this;
				self.tightkNots();
				self.el.remove();
				return self;			
			},
			/**
			 * Method used to remake connection in the post list ( dubled linked list )
			 *   when the post is removed from that position
			 */
			tightkNots: function()
			{
				if(this.next !== undefined)
					this.next.prev = this.prev;
				if(this.prev !== undefined)
					this.prev.next = this.next;				
			},			
			render: function()
			{
                            countLoaded++;
				var self = this, order = parseFloat(self.model.get('Order'));
				if ( !isNaN(self.order) && (order != self.order)) {
					var actions = {prev: 'insertBefore', next: 'insertAfter'}, ways = {prev: 1, next: -1}, anti = {prev: 'next', next: 'prev'}
					for( var dir = (self.order - order > 0)? 'next': 'prev', cursor=self[dir];
						(cursor[dir] !== undefined) && ( cursor[dir].order*ways[dir] < order*ways[dir] );
						cursor = cursor[dir]
					);
					var other = cursor[dir];
					if(other !== undefined)
						other[anti[dir]] = self;
					cursor[dir] = self;
					self.tightkNots();
					self[dir] = other;
					self[anti[dir]] = cursor;
					self.el[actions[dir]](cursor.el);
				}
				self.order = order;
				var content = self.model.get('Content');

				var style= '';                
				if (self.model.getClass() == 'wrapup') {
					style += ' open';
				}
				if (self.model.isService()) {
					style += ' ' + self.model.get('AuthorName');
                                        
                                        var meta = JSON.parse(self.model.get('Meta'));
                                        var annotation = '';
                                        if( meta.annotation) {
                                            for (var i=0; i < meta.annotation.length; i++ ) {
                                                if(meta.annotation[i]) {
                                                    annotation += meta.annotation[i];
                                                }
                                            }
                                        }
                                        
					if (self.model.get('AuthorName') == 'flickr') {
						var paddedContent = '<span>' + content + '</span>';
						var jqo = $(paddedContent);
						jqo.find('img').attr('src', jqo.find('a').attr('href'));
						content = jqo.html();
					} else if (self.model.get('AuthorName') == 'twitter') {        
						content = self.model.twitter.link.all(content);
					} else if (self.model.get('AuthorName') == 'google') {
                                            if (meta.tbUrl) {
                                                content += '<p><a href="' + meta.url + '"><img src="' + meta.tbUrl + '" height="' + meta.tbHeight + '" width="' + meta.tbWidth + '"></a></p>';
                                            }
                                        }
                                        
                                        content = annotation + content;
                                        
				}
				var postId = self.model.get('Id');
				var blogTitle = self._parent.model.get('Title');
				blogTitle = blogTitle.replace(/ /g, '-');
                                var hash = postId + '-' +  encodeURI (blogTitle);
                                var hash = postId;
                                var permalink = '<a rel="bookmark" href="#'+ hash +'">#</a>';
				var template ='<li class="'+ style +'"><a name="' + hash + '">' + content + '</a>&nbsp;'+ permalink +'</li>';
                                self.setElement( template );
			}
		}),
                totalLoad = 0,
                iidLoadTrace = 0,
                countLoaded = 0,
		TimelineView = $.gizmo.View.extend
		({
			el: '#livedesk-root',
			timeInterval: 10000,
			idInterval: 0,
			_latestCId: 0,
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
				this.model.sync();
				return this;
			},
			ensureStatus: function(){
				if(this.model.get('ClosedOn')) {
					var closedOn = new Date(this.model.get('ClosedOn'));
					//this.pause();
					this.model.get('PostPublished').pause();					
					this.el.find('#liveblog-status').html('The liveblog coverage was stopped '+closedOn.format('mm/dd/yyyy HH:MM:ss'));
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
				self.rendered = false;
				if($.type(self.url) === 'string')
					self.model = new Blog(self.url.replace('my/',''));				
				self.model.on('read', function()
				{ 
					if(!self.rendered) {
						self.model.get('PostPublished')
							.on('read', self.render, self)
							.on('update', self.addAll, self)
							.on('beforeUpdate', self.updateingStatus, self)
							.xfilter('CId').sync();
					}
					self.rendered = true;
				}).on('update', function(e, data){
					self.ensureStatus();
					self.renderBlog();
				});
				self.sync();				
			},
			addOne: function(model)
			{
				current = new PostItemView({model: model, _parent: this});
				this.el.find('#liveblog-post-list').prepend(current.el);
				current.next = this._latest;
				if( this._latest !== undefined )
					this._latest.prev = current;
				this._latest = current;
			},
			addAll: function(evt, data)
			{
				var i = data.length;
				while(i--) {
					this.addOne(data[i]);
				}
				this.updateStatus();				
			},
			updateingStatus: function()
			{
				this.el.find('#liveblog-status').html('updating...');
			},
			updateStatus: function()
			{
				var now = new Date();
				this.el.find('#liveblog-status').fadeOut(function(){
					$(this).text('updated on '+now.format('HH:MM:ss')).fadeIn();
				});
			},
			renderBlog: function()
			{
				$(this.el).find('article')
					//.find('h2').text(this.model.get('Title')).end()
					.find('p').text(this.model.get('Description'));
			},
                        
                        loadTrace: function() {
                            if ( countLoaded >= totalLoad) { 
                                this.gotoHash()
                                clearInterval(iidLoadTrace);
                            }
                        },
			render: function(evt)
			{				
				this.el.html('<article><h2></h2><p></p></article><div class="live-blog"><p class="update-time" id="liveblog-status"></p><div id="liveblog-posts"><ol id="liveblog-post-list" class="liveblog-post-list"></ol></div><div>');
				this.renderBlog();
				this.ensureStatus();
				data = this.model.get('PostPublished')._list;
				var next = this._latest, current, model, i = data.length;
                                
                                totalLoad = data.length;
                                var self = this;
                                iidLoadTrace = setInterval(function(){
                                    self.loadTrace();
                                }, 900)
				while(i--) {
					this.addOne(data[i]);
				}
                                
			}
			
		});
		window.livedesk.TimelineView = TimelineView;
		window.livedesk.callback();
	};
window.livedesk.init();
