define
([
    config.guiJs('superdesk/desks', 'task/common'),
    config.guiJs('superdesk/desks', 'models/desk')
], 
function(CommonViews, Desk)
{
    var desk = new Desk('http://localhost:8080/resources/Desk/Desk/1'),
        addView = new CommonViews.add;
    
    return {init: function(){ addView.setDesk(desk).activate(); }};
});