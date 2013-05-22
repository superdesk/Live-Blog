define([
    'jquery',
    'backbone',
    'router',
    'desk/models/desk-collection',
    'desk/views/single-desk',
    'angular',
    'desk/controllers/tasks',
    'desk/controllers/edit-task',
    'desk/resources',
    'desk/directives',
],
function($, Backbone, router, DeskCollection, DeskBoardsView, angular, TasksController, EditTaskController) {
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
        var template;
        $.tmpl('superdesk-desk>desk/single', {}, function(e, o) {
            template = o;
        });

        angular.module('desks', ['resources', 'directives']).
            controller('TasksController', ['$scope', 'desk', 'desks', 'tasks', 'Task', 'TaskService', TasksController]).
            controller('EditTaskController', ['$scope', 'Task', 'TaskStatusLoader', EditTaskController]).
            controller('CardController', function($scope, CardService) {
                CardService.getStatuses($scope.card).then(function(statuses) {
                    $scope.card.statuses = statuses;
                    $scope.isCardTask = function(task) {
                        for (var i in statuses) {
                            if (statuses[i].Key === task.Status.Key) {
                                return true;
                            }
                        }
                    };
                });
            }).
            controller('DeskController', function($scope, DeskService) {
                DeskService.getCards($scope.desk).then(function(cards) {
                    $scope.cards = cards;
                });
            }).
            config(['$routeProvider', function($routeProvider) {
                $routeProvider.
                    when('/desks/:deskId', {
                        controller: 'TasksController',
                        template: template,
                        resolve: {
                            desk: function(DeskLoader) {
                                return DeskLoader();
                            },
                            desks: function(DeskListLoader) {
                                return DeskListLoader();
                            },
                            tasks: function(DeskTaskLoader) {
                                return DeskTaskLoader();
                            }
                        }
                    });
            }]).
            config(['$interpolateProvider', function($interpolateProvider) {
                $interpolateProvider.startSymbol('{{ ');
                $interpolateProvider.endSymbol(' }}');
            }]);

        $('#area-main').attr('ng-view', '');
        angular.bootstrap('body', ['desks']);
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
