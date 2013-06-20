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
            link: function(scope, element, attrs) {
                var isChecked = '';
                if ($(element).attr('checked') == 'checked') {
                    isChecked = 'sf-checked';
                }
                $(element).wrap('<span class="sf-checkbox-custom ' + isChecked + '"></span>');
                $(element).hide();

                var setBg = $(element).attr('set-bg'); 
                if (typeof setBg !== undefined && setBg !== false && $(element).attr('checked') == 'checked') {
                    $(this).parents().eq(setBg).toggleClass('active-bg');
                }

                element.parent().on('click', function(e){
                    e.preventDefault();
                    $(this).toggleClass('sf-checked');

                    
                    
                    return false;
                });
                //*/
            }
        };
    });

});
