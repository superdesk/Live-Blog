requirejs.config({
    paths: {
        'superdesk/views': config.gui('superdesk/scripts/views'),
        'superdesk/models': config.gui('superdesk/scripts/models'),
        'desk': config.gui('superdesk-desk/scripts')
    }
});

define([
    'jquery',
    'router',
    'desk/views/config',
    'superdesk/views/menu',
    'angular',
    'desk/controllers/config-desks',
    'tmpl!superdesk-desk>config-desks'
], function($, router, configView, menuView, angular, ConfigDesksController) {
    'use strict';

    return {
        init: function(submenu, menu, data) {
            menuView.addItem(data.feed());

            // define router when we have menu url
            router.route(data.get('NavBar'), 'config:desks', function() {
                var module = angular.module('desks.config', ['resources', 'directives']);

                var template;
                $.tmpl('superdesk-desk>config-desks', {}, function(e, o) {
                    template = o;
                });

                module.config(['$routeProvider', function($routeProvider) {
                    $routeProvider.
                        when('/config/desks', {
                            controller: ConfigDesksController,
                            template: template,
                            resolve: {
                                desks: function(DeskListLoader) {
                                    return DeskListLoader();
                                },
                                statuses: function(TaskStatusLoader) {
                                    return TaskStatusLoader();
                                }
                            }
                        });
                }]);

                module.config(['$interpolateProvider', function($interpolateProvider) {
                    $interpolateProvider.startSymbol('{{ ');
                    $interpolateProvider.endSymbol(' }}');
                }]);

                module.controller('DeskController', function($scope, DeskService, CardService) {
                    $scope.desk.members = DeskService.getMembers($scope.desk);

                    DeskService.getCards($scope.desk).then(function(cards) {
                        $scope.desk.cards = cards;

                        $scope.removeFromAllCards = function(stat) {
                            angular.forEach($scope.desk.cards, function(card) {
                                for (var i in card.statuses) {
                                    if (card.statuses[i].Key === stat.Key) {
                                        CardService.removeStatus(card, stat);
                                        card.statuses.splice(i, 1);
                                        break;
                                    }
                                }
                            });
                        };
                    });
                });

                module.controller('CardController', function($scope, CardService) {
                    $scope.card.statuses = [];

                    CardService.getStatuses($scope.card).then(function(statuses) {
                        $scope.card.statuses = statuses;

                        $scope.findStatus = function(stat) {
                            var stats = $scope.card.statuses;
                            for (var i in stats) {
                                if (stats[i].Key === stat.Key) {
                                    return i;
                                }
                            }

                            return false;
                        };

                        $scope.hasStatus = function(stat) {
                            return $scope.findStatus(stat) !== false;
                        };

                        $scope.toggleStatus = function(card, stat) {
                            var index = $scope.findStatus(stat);
                            if (index !== false) {
                                CardService.removeStatus(card, stat);
                                $scope.card.statuses.splice(index, 1);
                            } else {
                                console.log('add', stat);
                                $scope.removeFromAllCards(stat);
                                CardService.addStatus(card, stat);
                                $scope.card.statuses.push(stat);
                            }
                        };
                    });
                });

                module.controller('AddMemberController', function($scope, DeskService) {
                    $scope.saveMembers = function(desk, users) {
                        angular.forEach(users, function(user) {
                            if (user.isSelected) {
                                DeskService.addMember(this, user);
                            }
                        }, desk);
                        desk.members = DeskService.getMembers(desk);
                    };
                });

                $('#area-main').attr('ng-view', '');
                angular.bootstrap('body', ['desks.config']);
            });
        }
    };
});
