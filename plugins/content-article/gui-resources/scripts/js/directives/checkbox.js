define([
    'angular',
    'jquery'
],
function(angular, $) {
    
    var module = angular.module('directives', ['resources']);

    module.directive('sdCheckbox', function() {
        return {
            restrict: 'A',
            link: function(scope, element, attrs) {
                console.log(element);
            }
        };
    });

});
