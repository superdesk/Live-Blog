 define(['gizmo/superdesk', 'gizmo/superdesk/models/action'], function(Gizmo, Action)
{
    var 
    actionUrlInst = null,
    rootUrl = null,
    actionUrl = Gizmo.Url.extend
    ({
        get: function()
        {
            var login = localStorage.getItem('superdesk.login.selfHref');
            this.data.url = login ? '/Action' : 'GUI/Action';
            this.data.root = login ? login : rootUrl;
            //console.log('url: ',this.data.url,'root: ',this.data.root);
            return Gizmo.Url.prototype.get.apply(this, arguments);
        }
    });
    actionUrlInst = new actionUrl('GUI/Action');
    rootUrl = actionUrlInst.data.root;
    return Gizmo.Collection.extend({ model: Action, href: actionUrlInst, syncAdapter: Gizmo.AuthSync });
});