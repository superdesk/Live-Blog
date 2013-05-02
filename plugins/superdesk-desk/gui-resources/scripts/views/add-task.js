define([
    'desk/views/common',
    'desk/models/gizmo/desk'
], function(CommonViews, Desk) {
    var desk = new Desk('http://localhost:8080/resources/Desk/Desk/1'),
        addView = new CommonViews.add;
    
    return {init: function(){ addView.setDesk(desk).activate(); }};
});
