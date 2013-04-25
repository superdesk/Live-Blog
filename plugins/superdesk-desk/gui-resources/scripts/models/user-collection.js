define([
    'backbone',
    'desk/models/user',
    'desk/utils'
], function(Backbone, User, utils) {
    return Backbone.Collection.extend({
        model: User,
        url: utils.getResourceUrl('HR/User'),
        xfilter: {'X-Filter': 'Id, FullName, Name, EMail'},

        parse: function(response) {
            return response.UserList;
        },

        comparator: function(user) {
            return user.getName().toLowerCase();
        }
    });
});
