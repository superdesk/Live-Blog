define(['angular'],
function(angular) {

    var module = angular.module('directives', []);

    module.directive('sfcheck', function() {
        return {
            restrict: 'E',
            replace: true,
            template : '<span class="sf-checkbox-custom" ng-class="{\'sf-checked\':check}" ></span>',
            scope: {
                check : "=",
                clickevent : "&"
            },
            link: function(scope, element, attrs, controller) {
                var scopeCaller = false;
                element.bind('click', function() {
                    scope.$apply(function(){
                        scope.check = !scope.check;
                        scopeCaller=true;
                    });
                });
                scope.$watch('check', function(value) {
                    scopeCaller ? (scopeCaller = false, scope.clickevent()) : '';
                });
            }
        };
    });

});
