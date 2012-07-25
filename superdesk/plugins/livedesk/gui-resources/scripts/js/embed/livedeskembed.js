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
        
        Posts = $.gizmo.Collection.extend({
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
                var self = this;
                this.post.on('update', this.render, this);
                this.post.on('read', this.render, this);
                this.post.sync();
            },
            render: function()
            {
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
                this.el.replaceWith( template );
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
                this.blog = new Blog('http://localhost:8080/resources/LiveDesk/Blog/1');
                var self = this;
                this.blog.on('read', function()
                { 
                    self.blog.get('Post').on('read', function(){
                        self.render();
                    })
                    self.blog.get('Post').xfilter('*').sync();
                });
                
                this.blog.sync();
            },
            render: function()
            {
                var self = this,i=0;
                this.blog.get('Post').each(function()
                {
                    var post = new Post(this.hash()), view = new PostItemView({
                        post: post
                    }); 
                    self.el.append( view.el );
                })
            }
            
        });
        
        new TimelineView({
            el: '#livedesk-root'
        });
    }
};
livedeskEmbed.init();

