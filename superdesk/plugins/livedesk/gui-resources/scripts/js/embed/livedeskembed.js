var livedeskEmbed = {
    jqueryLoaded : false,
    waited : 0,
    waitTime : 20, //miliseconds
    init : function() {
        if (typeof jQuery == 'undefined') {
            if(this.jqueryLoaded == false) {
                this.loadJquery(document, 'script', 'livedesk-jquery');
            }
            console.log('Waiting ' + this.waitTime);
            console.log(this.waited);
            this.waited += 1;
            
            if(this.waited > 50) {
                throw('waited too much');
            }
            setTimeout('livedeskEmbed.init()', this.waitTime);
        } else {
            this.startLoading();
        }
    },
    loadJquery : function(d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[1];
            if (d.getElementById(id)) return;
            js = d.createElement(s);js.id = id;
            js.src = "http://code.jquery.com/jquery-1.7.2.min.js";
            fjs.parentNode.insertBefore(js, fjs);
            this.jqueryLoaded = true;
            console.log('loading jQuery...');
            this.init();
    },
    
    startLoading : function() {
        //console.log('starting to load');
        //$('#loader-smack').html('merge jQuery');
        
        var 
        User = $.gizmo.Model.extend({}),
        Post = $.gizmo.Model.extend
        ({
            defaults:
            {
                Creator: User
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
        
        var 
        PostItemView = $.gizmo.View.extend
        ({
            init: function(href)
            {
                this.post = new Post(href);
                return this.render();
            },
            render: function()
            {
                // pus in ceva html 
                console.log(this.post.get('Content') );
                return '<div style="display:block">' + this.post.get('Content') + '</div>';
            }
        }),
        TimelineView = $.gizmo.View.extend
        ({
            events: 
            {
                '[uberclick="ceva-click-shucar"]': {'click': 'altceva'}
            },
            init: function(el)
            {
                this.el = el;
                this.blog = new Blog('http://localhost:8080/resources/LiveDesk/Blog/1');
                var self = this;
                this.blog.on('read', function()
                { 
                    self.blog.get('Post').on('read', function(){ self.render(); })
                    self.blog.get('Post').xfilter('*').sync();
                });
                
                this.blog.sync();
            },
            render: function()
            {
                var self = this;
                this.blog.get('Post').each(function()
                {
                    self.el.append( (new PostItemView).init(this.hash()) )
                })
            }
            
        });
        
        (new TimelineView).init($('#livedesk-root'));
    }
};
livedeskEmbed.init();

