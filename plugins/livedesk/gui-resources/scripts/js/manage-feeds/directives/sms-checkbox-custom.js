define([
	'angular',
    'lib/livedesk/scripts/js/manage-feeds/manage-feeds'
	],function(ngular, feeds){
        feeds.directive('smscustombox', function() {
            return {
                replace: true,
                template: '<span class="sf-checkbox-custom" ng-click="toggle(scope.sms)"></span>',
                link: function(scope, element, attrs) {
                    var customCheck = element;
                    var check = customCheck.parent().find('input[type="checkbox"]')
                    var parent = customCheck.parent();
                    //select blogs and check the custom
                    var myScope = scope;
                    var index = scope.$index;
                    if ( scope.sms.assigned ) {
                        customCheck.addClass('sf-checked');
                        parent.addClass('active-bg');
                    } 
                    
                    scope.toggle = function(para) {
                        customCheck.toggleClass('sf-checked');
                        parent.toggleClass('active-bg');
                        if ( scope.sms.assigned ) {
                            scope.sms.assigned = false;
                        } else {
                            scope.sms.assigned = true;
                        }
                        scope.$parent.handleChange(scope.sms);
                       
                    }
                }
            };
        });
});