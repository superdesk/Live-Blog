define([
    'superdesk/models/model',
    'desk/models/user-collection'
], function(Model, UserCollection) {
    return Model.extend({
        getView: function() {
            return {id: this.id, name: this.get('Name')};
        },

        parse: function(response) {
            this.url = response.href;
            delete response.href;

            try {
                this.users = new UserCollection([], {url: response.User.href});
                this.unassignedUsers = new UserCollection([], {url: response.UserUnassigned.href});
            } catch(err) {
                if (err instanceof TypeError) {
                    // TODO fix xfilter for POST requests
                    return response;
                }

                throw err;
            }

            return response;
        }
    });
});
