define([ 'gizmo/superdesk', 
    config.guiJs('livedesk', 'models/user'),
    config.guiJs('livedesk', 'models/language'),
    config.guiJs('livedesk', 'models/posts'),
    config.guiJs('livedesk', 'models/collaborators')],
function(Gizmo, User, Language, Posts, Collaborators) 
{
    // Blog
    return Gizmo.Model.extend
    ({
        // TODO this is not the real model path. should be LiveDesk/Blog
		url: new Gizmo.Url('Blog'),
        defaults:
        { 
            Creator: User,
            Language: Language,
            Collaborator: Collaborators,
            Post: Posts,
            PostPublished: Posts,
            PostUnpublished: Posts
        },
        putLive: function()
        {
            var putLiveHref = this.href+'/PutLive';
            var self = this,
                dataAdapter = function()
                { 
                    return self.syncAdapter.request.apply(self.syncAdapter, arguments); 
                },
                ret = dataAdapter(putLiveHref).update();
            this.triggerHandler('putlive');
            return ret;
        }
    }, 
    { register: 'Blog' } );
});