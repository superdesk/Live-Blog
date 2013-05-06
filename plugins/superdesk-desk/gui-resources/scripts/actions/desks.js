requirejs.config({
    paths: {
        'angular': 'https://ajax.googleapis.com/ajax/libs/angularjs/1.0.6/angular',
        'angular-resource': 'http://code.angularjs.org/1.0.6/angular-resource'
    },
    shim: {
        'angular': {exports: 'angular'},
        'angular-resource': {deps: ['angular']}
    }
});

define([
    'jquery',
    'backbone',
    'router',
    'desk/models/desk-collection',
    'desk/views/single-desk',
    'angular',
    'desk/controllers/desks',
    'desk/services/resource'
],
function($, Backbone, router, DeskCollection, DeskBoardsView, angular, TasksController) {
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
        $('#area-main').tmpl('superdesk-desk>desk/single').
            attr('ng-controller', 'TasksController');

        angular.module('desks', ['resources']).
            value('routeParams', {deskId: deskId}).
            controller('TasksController', ['$scope', 'routeParams', 'Desk', 'TaskList', 'Task', TasksController]);

        angular.bootstrap('#area-main', ['desks']);
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
