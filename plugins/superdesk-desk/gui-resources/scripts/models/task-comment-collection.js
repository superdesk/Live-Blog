define([
    'backbone',
    'desk/models/task-comment',
    'desk/utils'
], function(Backbone, TaskComment, utils) {
    return Backbone.Collection.extend({
        model: TaskComment,
        url: utils.getResourceUrl('TaskComment/TaskComment'),
        xfilter: {'X-Filter': 'Id, *, User.*'},

        parse: function(response) {
            return response.TaskCommentList;
        },

        comparator: function(task) {
            return task.id;
        }
    });
});
