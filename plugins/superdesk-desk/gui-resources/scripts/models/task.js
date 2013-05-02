define([
    'superdesk/models/model',
    'desk/utils'
], function(Model, utils) {
    return Model.extend({
        idAttribute: 'Id',

        urlRoot: utils.getResourceUrl('Desk/Task'),

        defaults: {
            Status: 'to do'
        },

        getView: function() {
            return {
                'Id': this.get('Id'),
                'Title': this.get('Title')
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
