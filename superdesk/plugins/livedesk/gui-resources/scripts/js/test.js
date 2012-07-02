define(['gizmo/superdesk'], 
function(giz)
{
    giz.Model.prototype.syncAdapter.href = function(source)
    {
        return 'http://localhost:8080/resources/'+source;
    };
    giz.AuthModel.prototype.syncAdapter.href = function(source)
    {
        return 'http://localhost:8080/resources/my/'+source;
    };
    giz.Collection.prototype.syncAdapter.href = function(source)
    {
        return 'http://localhost:8080/resources/'+source;
    };

    var PostType = giz.Model.extend({}),
        PostTypes = new giz.Collection('Superdesk/PostType'),
        Posts = new giz.Collection(),
        PostOwned = new giz.Collection(),
        PostPublished = new giz.Collection(),
        PostUnpublished = new giz.Collection(),
        User = giz.Model.extend(),
        Language = giz.Model.extend(),
        Blog = giz.AuthModel.extend({ defaults: 
        {
            Post: Posts,
            PostOwned: PostOwned,
            PostPublished: PostPublished,
            PostUnpublished: PostUnpublished,
            Creator: User,
            Language: Language
        }});
    
    EditApp = function( theBlog ){ this.init( theBlog ); };
    EditApp.prototype = 
    {
        init: function(theBlog)
        {
            theBlog = 'LiveDesk/Blog/1';
            this.blogHref = theBlog;
            blogHref = theBlog;
            this.render();
        },
        render: function()
        {
            var self = this;
            $(PostTypes).on('read', function(){ self.prerender(this.getList()); });
            PostTypes.xfilter('Key').sync();
        },
        prerender: function(postTypes)
        {
            var b = new Blog(this.blogHref);
            
            $(b).on('read', function()
            {
                console.log(this, arguments);
            });
            b.xfilter('Creator.Name', 'Creator.Id').sync();
        }
    };
    
    new EditApp;
});