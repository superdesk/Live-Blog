define([
    'angular',
    'jquery'
],
function(angular, $) {
    
    var module = angular.module('directives', ['resources']);

    module.directive('sdCheckbox', function() {
        return {
            restrict: 'A',
            requires: 'ngModel',
            scope: false,
            link: function(scope, element, attrs) {
                
            }
        };
    });

});
