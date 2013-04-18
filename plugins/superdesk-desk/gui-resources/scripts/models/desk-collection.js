define([
    'backbone',
    'desk/models/desk',
    'desk/utils'
], function(Backbone, Desk, utils) {
    return Backbone.Collection.extend({
        model: Desk,
        url: utils.getResourceUrl('Desk/Desk'),
        xfilter: {'X-Filter': 'Id, Name, User'},

        parse: function(response) {
            return response.DeskList;
        }
    });
});
