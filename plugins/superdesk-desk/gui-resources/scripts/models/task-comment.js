define([
    'superdesk/models/model',
    'desk/utils'
], function(Model, utils) {
    return Model.extend({
        idAttribute: 'Id',

        urlRoot: utils.getResourceUrl('Desk/TaskComment'),

        defaults: {},

        getView: function() {
            return {
                'Id': this.get('Id'),
                'Text': this.get('Text'),
                'User': this.get('User'),
                'Date': this.get('UpdatedOn')
            };
        },

        parse: function(response) {
            if (response && 'href' in response) {
                this.url = response.href;
                delete response.href;
            }

            return response;
        }
    });
});
