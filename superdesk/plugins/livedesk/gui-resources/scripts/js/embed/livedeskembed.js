function isOnly(data,key) {
	var count = 0;
	for(i in data) {
		count++;
		if(count>1) return false;
	};
	return (data !== undefined) && (data[key] !== undefined) && (count == 1);
}

var livedeskEmbed = {
    init : function() {
        var self = this;
        if (typeof jQuery == 'undefined') {
            self.loadScript('http://code.jquery.com/jquery-1.7.2.min.js', function(){
                if (typeof $.gizmo == 'undefined') {
                    self.loadScript('gizmo.js', function(){
                        self.startLoading();
                    })
                }
            })
        } else {
            if (typeof $.gizmo == 'undefined') {
                self.loadScript('gizmo.js', function(){
                    self.startLoading();
                })
            } else {
                self.startLoading();
            }
        }
    },
    
    loadScript : function (src, callback) {
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
    },
    startLoading : function() {
        var 
        User = $.gizmo.Model.extend({}),
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
			getMaximumCid: function(models){
				for (var i in models) {
					var items = models[i];
					break;
				}
				for(i=0, count=items.length; i<count; i++) {
					if( this._latestCId < parseInt(items[i].CId) )
						this._latestCId = parseInt(items[i].CId);
				}
			},
			auto: function(){
				var self = this;
				this.sync({data: {'startEx.cId': this._latestCId}, headers: { 'X-Filter': 'CId'}}).done(function(models){
					self.getMaximumCid(models);
				});
				return this;
			},                                                                                                                                                                                                                                                                              
			pause: function(){
				var self=this;
				clearInterval(self.idInterval);
			},
			start: function(){
				var self = this;
				this.auto().setIdInterval(function(){self.auto();});
			}
		});        
        Posts = AutoCollection.extend({
            model: Post
        }),
       
        Blog = $.gizmo.Model.extend
        ({
            defaults: 
            {
                Post: Posts,
                PostPublished: Posts,
                PostUnpublished: Posts
            }
        });
        
        var i=0,
        PostItemView = $.gizmo.View.extend
        ({
            init: function()
            {
                this.post.on('update', function(evt, data){
					if(isOnly(data, 'CId'))
						this.post.xfilter(self.xfilter).sync();
					else
						this.render();
				}, this);
                this.post.on('read', this.render, this);
				this.post.on('remove', this.remove, this);
                this.post.sync();
            },
			remove: function()
			{
				this.el.remove();
				return this;			
			},
            render: function()
            {
				var self = this, order = parseInt(this.post.get('Order'));
				if ( !isNaN(self.order) && (order != self.order)) {
					var actions = { prev: 'insertBefore', next: 'insertAfter' }, ways = { prev: 1, next: -1};
					for( var dir = (self.order - order > 0)? 'next': 'prev', cursor=self[dir]; 
						(cursor[dir] !== undefined) && ( cursor[dir].order*ways[dir] < order*ways[dir] ); 
						cursor = cursor[dir]
					);
					self.el[actions[dir]](cursor.el);
				}
				self.order = order;
                var content = this.post.get('Content');

                var style= '';                
                if (this.post.getClass() == 'wrapup') {
                    style += ' open';
                }
                if (this.post.isService()) {
                    style += ' ' + this.post.get('AuthorName');
                    if (this.post.get('AuthorName') == 'flickr') {
                        var paddedContent = '<span>' + content + '</span>';
                        var jqo = $(paddedContent);
                        jqo.find('img').attr('src', jqo.find('a').attr('href'));
                        content = jqo.html();
                    } else if (this.post.get('AuthorName') == 'twitter') {
                        content = this.post.twitter.link.all(content);
                    }
                }
                var template = '<li class="'+ style +'">' + content + '</li>';
                this.setElement( template );
            }
        }),
        TimelineView = $.gizmo.View.extend
        ({
            events: 
            {
                '[uberclick="ceva-click-shucar"]': {
                    'click': 'altceva'
                }
            },
            init: function()
            {
                this.blog = new Blog('http://localhost:8082/resources/LiveDesk/Blog/1');
                var self = this;
                this.blog.on('read', function()
                { 
                    self.blog.get('PostPublished').on('read', function(){
						self.render();
                    }).xfilter('CId').start();
                });
                this.blog.sync();
            },
            render: function()
            {
                var self = this, i=0, prev = undefined;;
                this.blog.get('PostPublished').each(function(key, post)
                {
						if(post.view === undefined) {
							var view = new PostItemView({
								post: post
							});
							post.view = view;
							view.prev = prev;
							if( prev !== undefined )
								prev.next = view;
							prev = view;
							self.el.append( view.el );
						}
                })
            }
            
        });
        
        new TimelineView({
            el: $('#livedesk-root')
        });
    },
};
livedeskEmbed.init();

