var livedeskEmbed = {
    jqueryLoaded : false,
    gizmoLoaded : false,
    waited : 0,
    waitTime : 20, //miliseconds
    init : function() {
        
        //make sure jsLib is loaded
        if (typeof jQuery == 'undefined') {
            if(this.jqueryLoaded == false) {
                this.loadScript(document, "http://code.jquery.com/jquery-1.7.2.min.js", 'livedesk-jquery');
            }
            setTimeout('livedeskEmbed.init()', this.waitTime);
        } else {   
            if (typeof $.gizmo == 'undefined') {
                if(this.gizmoLoaded == false) {
                    this.loadScript(document, "gizmo.js", 'livedesk-gizmo');
                }
                setTimeout('livedeskEmbed.init()', this.waitTime);
            } else {
                this.startLoading();
            }
        }
    },
    loadScript : function(d, src, id) {
            
            var js, fjs = d.getElementsByTagName('script')[1];
            if (d.getElementById(id)) return;
            js = d.createElement('script');js.id = id;
            js.src = src;
            fjs.parentNode.insertBefore(js, fjs);
            this.jqueryLoaded = true;
            console.log('loading ' + src);
            this.init();
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
        
        Posts = $.gizmo.Collection.extend({model: Post}),
        
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
                    //$(this.el).addClass('open');
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
                '[uberclick="ceva-click-shucar"]': {'click': 'altceva'}
            },
            init: function()
            {
                this.blog = new Blog('http://localhost:8080/resources/LiveDesk/Blog/1');
                var self = this;
                this.blog.on('read', function()
                { 
                    self.blog.get('Post').on('read', function(){self.render();})
                    self.blog.get('Post').xfilter('*').sync();
                });
                
                this.blog.sync();
            },
            render: function()
            {
                var self = this,i=0;
                this.blog.get('Post').each(function()
                {
                    
                    var post = new Post(this.hash()), view = new PostItemView({ post: post }); 
                    self.el.append( view.el );
                })
            }
            
        });
        
        new TimelineView({ el: '#livedesk-root'});
    }
};
livedeskEmbed.init();

