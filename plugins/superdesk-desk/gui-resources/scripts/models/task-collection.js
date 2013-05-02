define([
    'backbone',
    'desk/models/task',
    'desk/utils'
], function(Backbone, Task, utils) {
    return Backbone.Collection.extend({
        model: Task,
        xfilter: {'X-Filter': 'Id, *'},

        parse: function(response) {
            return response.TaskList;
        },

        comparator: function(task) {
            return -1 * task.id;
        }
    });
});
