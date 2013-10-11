define([
	'angular',
    'lib/livedesk/scripts/js/manage-feeds/manage-feeds'
	],function(ngular, feeds){
        feeds.directive('custombox', function() {
            return {
                replace: true,
                template: '<span class="sf-checkbox-custom" ng-click="toggle()"></span>',
                link: function(scope, element, attrs) {
                    var customCheck = element;
                    var check = customCheck.parent().find('input[type="checkbox"]')
                    var parent = customCheck.parent();
                    //select blogs and check the custom

                    if ( scope.blog.chained ) {
                        customCheck.addClass('sf-checked');
                        parent.addClass('active-bg');
                    }
                    
                    scope.toggle = function() {
                        customCheck.toggleClass('sf-checked');
                        parent.toggleClass('active-bg');
                        if ( scope.blog.chained ) {
                            scope.blog.chained = false;
                        } else {
                            scope.blog.chained = true;
                        }
                        scope.$parent.$parent.chainChange(scope.blog, scope.$parent.chain.URI.href, scope.$parent.$index, scope.$index)
                       
                    }
                }
            };
        });
});