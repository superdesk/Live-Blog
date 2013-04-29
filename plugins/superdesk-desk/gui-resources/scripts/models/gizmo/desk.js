define
([
    'gizmo/superdesk', 
    config.guiJs('superdesk/user', 'models/user')
], 
function(giz, User)
{ 
    return giz.Model.extend
    ({
        url: new giz.Url('Desk/Desk'),
        defaults:
        {
            User: giz.Collection.extend({ model: User })
        }
    });
});