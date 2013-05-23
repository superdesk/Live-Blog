define([
    'angular',
    'jquery',
    'jqueryui/datepicker',
    'jqueryui/sortable'
],
function(angular, $) {
    'use strict';

    var module = angular.module('directives', ['resources']);

    module.directive('sdDatepicker', function() {
        return {
            restrict: 'A',
            requires: 'ngModel',
            link: function(scope, element, attrs) {
                element.datepicker({
                    dateFormat: 'yy-mm-dd 12:00:00',
                    onClose: function(dateText) {
                        scope.$apply(function() {
                            element.controller('ngModel').$setViewValue(dateText);
                        });
                    }
                });
                element.addClass('hide');
                element.siblings('[data-toggle="datepicker"]').click(function() {
                    element.datepicker('show');
                });
            }
        };
    });

    module.directive('sdUserImage', function(UserService) {
        return {
            restrict: 'A',
            template: '<img ng-src="{{ src }}" width="{{ width }}" height="{{ height }}" alt="{{ alt }}" />',
            scope: {user: '=sdUser'},
            link: function(scope, element, attrs) {
                scope.width = attrs.width;
                scope.height = attrs.height;
                scope.$watch('user', function(user) {
                    if (user) {
                        scope.alt = user.Name;
                        UserService.getImage(user).then(function(image) {
                            scope.src = image.Thumbnail.href;
                        }, function() {
                            scope.src = '/content/lib/core/images/avatar_default_collaborator.png';
                        });
                    } else {
                        scope.alt = null;
                        scope.src = null;
                    }
                });
            }
        };
    });

    module.directive('sdSortable', function() {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function(scope, element, attrs) {
                var ngModel = element.controller('ngModel');
                var startIndex = NaN;
                $(element[0]).sortable({
                    delay: 150,
                    start: function(e, ui) {
                        startIndex = $(ui.item).index();
                    },
                    stop: function(e, ui) {
                        var stopIndex = $(ui.item).index();
                        var list = ngModel.$modelValue;
                        console.log(list[startIndex], list[stopIndex]);
                    }
                });
            }
        };
    });
});
