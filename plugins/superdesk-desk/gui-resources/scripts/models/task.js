define([
    'superdesk/models/model',
    'desk/models/task-comment-collection',
    'desk/utils'
], function(Model, TaskCommentCollection, utils) {
    return Model.extend({
        idAttribute: 'Id',

        urlRoot: utils.getResourceUrl('Desk/Task'),

        defaults: {
            Status: 'to do'
        },

        getView: function() {
            return {
                'Id': this.get('Id'),
                'Title': this.get('Title'),
                'Comments': this.get('Comments')
            };
        },

        parse: function(response) {
            var self = this;

            if (response && 'href' in response) {
                this.url = response.href;
                delete response.href;
            }

            //TODO: ideally this should not be done this way
            this.comments = new TaskCommentCollection([], {url: this.url + '/TaskComment'});
            //this.comments = new TaskCommentCollection([], {url: response.TaskComments.href});

            return response;
        }
    });
});
