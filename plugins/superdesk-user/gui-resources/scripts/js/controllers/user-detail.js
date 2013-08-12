define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, UserDetailLoader) {
        
        $scope.initialize = function() {
            $scope.$watch('selectedUserId', function(selectedUserId) {
                if (selectedUserId !== null) {
                    $scope.loadUser(selectedUserId);
                }
            });
        };

        $scope.loadUser = function(userId) {
            $scope.user = UserDetailLoader(userId);
            $('.user-details-pane').addClass('open');
        };

        $scope.unloadUser = function() {
            $scope.$parent.selectedUserId = null;
            $scope.user = {};
            $('.user-details-pane').removeClass('open');
        };

        //
        $scope.initialize();

    };
});
