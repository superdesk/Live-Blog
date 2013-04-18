define
([
    'gizmo/superdesk',
    config.guiJs('superdesk/user', 'models/user'),
    config.guiJs('superdesk/desks', 'models/desk')
], 
function(giz, User, Desk)
{ 
    return giz.Model.extend
    ({
        defaults: 
        { 
            Desk: Desk,
            User: User
        },
        url: new giz.Url('Desk/Task'),
    });
});