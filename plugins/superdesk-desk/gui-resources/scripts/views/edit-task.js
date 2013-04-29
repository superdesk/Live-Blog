define
([
    config.guiJs('superdesk/desks', 'task/common'),
    config.guiJs('superdesk/desks', 'models/task')
], 
function(CommonViews, Task)
{
    var task = new Task('http://localhost:8080/resources/Desk/Task/18'),
        editView = new CommonViews.edit;
        
    return {init: function(){ editView.setTask(task).activate(); }};
});