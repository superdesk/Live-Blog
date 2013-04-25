define([
    'superdesk/models/model'
], function(Model) {
    return Model.extend({
        getData: function() {
            return {
                name: this.getName(),
                email: this.get('EMail'),
                id: this.id,
                selected: this.get('selected')
            };
        },

        getName: function() {
            if (this.get('FullName')) {
                return this.get('FullName');
            } else {
                return this.get('Name');
            }
        },

        getResource: function() {
            return {
                Id: this.id,
                FullName: this.get('FullName'),
                Name: this.get('Name'),
                EMail: this.get('Email')
            };
        }
    });
});
