define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, User, UserListLoader) {
        
        $scope.initialize = function() {
            $('body').removeClass().addClass('users'); // hack, should be removed after templates are fixed

            $scope.loadSettings();

            $scope.selectedUserId = null;

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
                    itemsPerPage: 25,
                    fields: {
                        avatar: true,
                        name: true,
                        username: true,
                        email: true,
                        group: true,
                        contributor: true,
                        since: true,
                        permissions: true
                    }
                };
            }
        };

        $scope.toggle = function(index) {
            if ($scope.users[index].checked === false) {
                $scope.allChecked = false;
            } else {
                var allChecked = true;
                for (var i = 0; i < $scope.users.length; i = i + 1) {
                    if ($scope.users[i].checked === false) {
                        allChecked = false;
                    }
                }
                $scope.allChecked = allChecked;
            }
        };
        $scope.toggleAll = function() {
            for (var i = 0; i < $scope.users.length; i = i + 1) {
                $scope.users[i].checked = $scope.allChecked;
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
