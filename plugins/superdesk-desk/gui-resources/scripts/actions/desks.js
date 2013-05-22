define([
    'jquery',
    'backbone',
    'router',
    'desk/models/desk-collection',
    'angular',
    'desk/controllers/tasks',
    'desk/controllers/edit-task',
    'desk/controllers/card',
    'desk/controllers/desk',
    'desk/resources',
    'desk/directives',
    'tmpl!superdesk-desk>desk/single'
],
function($, Backbone, router, DeskCollection, angular, TasksController, EditTaskController, CardController, DeskController) {
    var DeskMenuView = Backbone.View.extend({
        tagName: 'li',
        render: function() {
            var link = $('<a />').text(this.model.get('Name')).attr('href', '#desks/' + this.model.id);
            $(this.el).html(link);
            return this;
        }
    });

    var MenuView = Backbone.View.extend({
        initialize: function() {
            this.collection.on('reset', this.render, this);
        },

        render: function() {
            var list = $(this.el).empty();
            this.collection.each(function(desk) {
                var view = new DeskMenuView({model: desk});
                list.append(view.render().el);
            });
        }
    });

    router.route('desks/:id', 'desk', function singleDesk(deskId) {
        var module = angular.module('desks', ['resources', 'directives']);

        module.controller('TasksController', TasksController);
        module.controller('EditTaskController', EditTaskController);
        module.controller('CardController', CardController);
        module.controller('DeskController', DeskController);

        module.config(['$interpolateProvider', function($interpolateProvider) {
            $interpolateProvider.startSymbol('{{ ');
            $interpolateProvider.endSymbol(' }}');
        }]);

        angular.module('resources').value('deskId', deskId);

        $('#area-main').tmpl('superdesk-desk>desk/single');
        $('#area-main').attr('ng-controller', 'TasksController');
        angular.bootstrap(document, ['desks']);
    });

    router.route('desks', 'desks', function allDesks() {
    });

    return {
        init: function(submenu, menu, data) {
            var desks = new DeskCollection();
            var menu = new MenuView({el: submenu, collection: desks});
            var timeout = 5000;

            function fetchDesks() {
                desks.fetch({reset: true, headers: desks.xfilter});
                setTimeout(fetchDesks, timeout);
            };

            desks.xfilter = {'X-Filter': 'Id, Name'};
            fetchDesks();
        }
    };
});
