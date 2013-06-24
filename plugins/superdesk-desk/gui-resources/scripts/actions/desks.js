define([
    'jquery',
    'backbone',
    'router',
    'desk/models/desk-collection',
    'angular',
    'desk/resources',
    'desk/directives',
    config.guiJs('media-archive', 'resources'),
    'desk/controllers/tasks',
    'desk/controllers/edit-task',
    'desk/controllers/card',
    'desk/controllers/desk',
    'desk/controllers/master',
    'desk/controllers/desks',
    'desk/controllers/task',
    'desk/controllers/attach-file',
    'tmpl!superdesk-desk>single-desk',
    'tmpl!superdesk-desk>master-desk'
],
function($, Backbone, router, DeskCollection, angular) {
    var DeskMenuView = Backbone.View.extend({
        tagName: 'li',
        render: function() {
            var link = $('<a />').text(this.model.get('Name')).attr('href', '#/desks/' + this.model.get('Id'));
            $(this.el).html(link);
            return this;
        }
    });

    var MenuView = Backbone.View.extend({
        initialize: function() {
            this.collection.on('reset', this.render, this);
            this.allDesksModel = new Backbone.Model({
                Name: _('All Desks'),
                Id: ''
            });
        },

        render: function() {
            var list = $(this.el).empty();

            var allDesksView = new DeskMenuView({model: this.allDesksModel});
            list.append(allDesksView.render().el);
            if (this.collection.length) {
                list.append($('<li />').addClass('divider'));
            }

            this.collection.each(function(desk) {
                var view = new DeskMenuView({model: desk});
                list.append(view.render().el);
            });
        }
    });

    var module = angular.module('desks', ['desks.resources', 'desks.directives', 'superdesk.media-archive.resources']);
    module.config(['$interpolateProvider', function($interpolateProvider) {
        $interpolateProvider.startSymbol('{{ ');
        $interpolateProvider.endSymbol(' }}');
    }]);

    module.controller('TasksController', require('desk/controllers/tasks'));
    module.controller('EditTaskController', require('desk/controllers/edit-task'));
    module.controller('CardController', require('desk/controllers/card'));
    module.controller('DeskController', require('desk/controllers/desk'));
    module.controller('MasterController', require('desk/controllers/master'));
    module.controller('DesksController', require('desk/controllers/desks'));
    module.controller('TaskController', require('desk/controllers/task'));
    module.controller('AttachFileController', require('desk/controllers/attach-file'));

    router.route('desks/:id', 'desk', function singleDesk(deskId) {
        angular.module('desks.resources').value('deskId', deskId);
        $('#area-main').tmpl('superdesk-desk>single-desk');
        $('#area-main').attr('ng-controller', 'TasksController');
        angular.bootstrap(document, ['desks']);
    });

    router.route('desks/', 'desks', function allDesks() {
        $('#area-main').tmpl('superdesk-desk>master-desk');
        $('#area-main').attr('ng-controller', 'MasterController');
        angular.bootstrap(document, ['desks']);
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
