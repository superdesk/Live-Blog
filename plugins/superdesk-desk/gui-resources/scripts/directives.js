define([
    'angular',
    'jquery',
    'jqueryui/datepicker',
    'jqueryui/sortable'
],
function(angular) {
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
                element.sortable({
                    update: function(e, ui) {
                        console.log(element.sortable('toArray', ['data-index']));
                    }
                });
            }
        };
    });
});
