define([
    'superdesk/models/model',
    'desk/models/user-collection'
], function(Model, UserCollection) {
    return Model.extend({
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
                this.unassignedUsers = new UserCollection([], {url: response.UserUnassigned.href});
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
