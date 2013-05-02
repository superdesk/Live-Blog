define([
    'superdesk/models/model',
    'desk/models/user-collection',
    'desk/models/task-collection',
    'desk/utils'
], function(Model, UserCollection, TaskCollection, utils) {
    return Model.extend({
        urlRoot: utils.getResourceUrl('Desk/Desk'),

        getView: function() {
            return {id: this.id, name: this.get('Name')};
        },

        validate: function(attrs, options) {
            if (!attrs.Name) {
                return _("Please provide a name");
            }
        },

        parse: function(response) {
            if (response === null) { // after put
                return;
            }

            if ('href' in response) { // after post
                this.url = response.href;
                delete response.href;
            }

            try {
                this.users = new UserCollection([], {url: response.User.href});
                delete response.User;

                this.unassignedUsers = new UserCollection([], {url: response.UserUnassigned.href});
                delete response.UserUnassigned;

                this.tasks = new TaskCollection([], {url: response.Task.href});
                delete response.Task;
            } catch(err) {
                // TODO fix xfilter for POST requests
                if (err instanceof TypeError) {
                    return response;
                }

                throw err;
            }

            return response;
        }
    });
});
