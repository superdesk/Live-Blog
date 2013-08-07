define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, User, UserListLoader) {
        
        $scope.initialize = function() {
            $scope.loadSettings();

            $scope.pageMax = 1;
            $scope.page = 1;

            $scope.$watch('page', function(page) {
                $scope.loadUsers();
            });
            $scope.$watch('settings', function(settings, oldSettings) {
                $scope.saveSettings();
                if (settings.itemsPerPage !== oldSettings.itemsPerPage) {
                    $scope.loadUsers();
                }
            }, true);
            $scope.$watch('users', function(users){
                console.log(users);
                if (users !== undefined) {
                    $scope.pageMax = Math.ceil(users.count / $scope.settings.itemsPerPage);
                    if ($scope.pageMax === 0) {
                        $scope.pageMax = 1;
                    }
                    delete users.count;
                    $scope.users = users;
                }
            });
            $scope.$watch('searchTerm', function(searchTerm){
                if (searchTerm === undefined) {
                    searchTerm = '';
                }
                $scope.loadUsers();
            });
        };

        $scope.saveSettings = function() {
            localStorage.setItem('superdesk.userList.settings', angular.toJson($scope.settings));
        };
        $scope.loadSettings = function() {
            $scope.settings = angular.fromJson(localStorage.getItem('superdesk.userList.settings'));
            if ($scope.settings === null) {
                $scope.settings = {
                    itemsPerPage: 25
                };
            }
        };

        $scope.loadUsers = function() {
            var limit = $scope.settings.itemsPerPage;
            var offset = ($scope.page - 1) * limit;

            $scope.users = UserListLoader(offset, limit, $scope.searchTerm);
        };

        //

        $scope.initialize();

    };
});
