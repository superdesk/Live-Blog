define([
    'backbone',
    'desk/models/desk',
    'desk/utils'
], function(Backbone, Desk, utils) {
    return Backbone.Collection.extend({
        model: Desk,
        url: utils.getResourceUrl('Desk/Desk'),
        xfilter: {'X-Filter': '*,User'},

        parse: function(response) {
            return response.DeskList;
        },

        comparator: function(desk) {
            return -1 * desk.get('Id');
        }
    });
});
