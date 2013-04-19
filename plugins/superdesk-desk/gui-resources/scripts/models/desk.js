define([
    'superdesk/models/model',
    'desk/models/user-collection'
], function(Model, UserCollection) {
    return Model.extend({
        parse: function(response) {
            this.users = new UserCollection([], {url: response.User.href});
            this.unassignedUsers = new UserCollection([], {url: response.UserUnassigned.href});
            return response;
        }
    });
});
