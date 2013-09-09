define(['angular'],
function(angular) {

    var module = angular.module('directives', []);

    //use <sfcheck check="modelVariable" clickevent="OnClickEventListener" />
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

    //use <sftoggle check="modelVariable" clickevent="OnClickEventListener" />
    //for on/off type of toggle use attribute  >>  onoff="true" 
    module.directive('sftoggle', function() {
        return {
            restrict: 'E',
            replace: true,
            template : '<div class="sf-toggle-custom" ng-class="{\'sf-checked\':check, \'on-off-toggle\' : onoff}"><div class="sf-toggle-custom-inner"></div></div>',
            scope: {
                check : "=",
                clickevent : "&",
                onoff : "="
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
