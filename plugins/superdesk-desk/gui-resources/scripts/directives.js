define([
    'angular',
    'jquery',
    'jqueryui/datepicker'
],
function(angular, $) {
    angular.module('directives', []).
        directive('sdDatepicker', function() {
            return {
                restrict: 'A',
                link: function($scope, $element, $attrs) {
                    $element.addClass('hide');
                    $element.datepicker({
                        dateFormat: 'yy-mm-dd 12:00:00',
                        onClose: function(dateText) { $scope.$apply($attrs['ngModel'] + '="' + dateText + '"'); }
                    });
                    $element.siblings('[data-toggle="datepicker"]').click(function() {
                        $element.datepicker('show');
                    });
                }
            };
        });
});
