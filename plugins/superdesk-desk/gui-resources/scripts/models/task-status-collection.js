define([
    'backbone',
    'desk/models/desk',
    'desk/utils'
], function(Backbone, Desk, utils) {
    return Backbone.Collection.extend({
        url: utils.getResourceUrl('Desk/TaskStatus'),
        xfilter: {'X-Filter': 'Id, Name'},

        parse: function(response) {
            return response.TaskStatusList;
        }
    });
});
