define([
    'angular',
    'jquery',
    'jqueryui/datepicker'
],
function(angular) {
    'use strict';

    angular.module('directives', []).
        directive('sdDatepicker', function() {
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
});
