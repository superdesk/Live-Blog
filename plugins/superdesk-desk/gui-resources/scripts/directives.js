define([
    'angular',
    'jquery',
    'jqueryui/datepicker',
    'jqueryui/sortable'
],
function(angular, $) {
    'use strict';

    var module = angular.module('directives', []);

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
