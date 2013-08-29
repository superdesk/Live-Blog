define([
    'angular',
    'utils/sha512',
],
function(angular, sha) {
    'use strict';

    return function($scope, $q, User, UserDetailLoader, RoleListLoader) {
        
        $scope.initialize = function() {
            $scope.enabled = false;

            $scope.roleList = RoleListLoader();
            
            $scope.$watch('selectedUserId', function(selectedUserId) {
                if (selectedUserId === 0) {
                    $scope.newUser = {roles: {}};
                    for (var i in $scope.roleList) {
                        $scope.newUser.roles[$scope.roleList[i].Id] = false;
                    }
                    $scope.enabled = true;
                    $('#profile-button').tab('show');
                    $('#edit-profile-button').tab('show');
                } else if (selectedUserId !== null) {
                    $('#overview-button').tab('show');
                    $scope.loadUser(selectedUserId);
                }
            });
            $scope.$watch('user', function(user){
                if (user !== undefined) {
                    user.roles = {};
                    for (var i in $scope.roleList) {
                        user.roles[$scope.roleList[i].Id] = false;
                        var status = false;
                        for (var j in user.roleList) {
                            if (user.roleList[j].Id === $scope.roleList[i].Id) {
                                status = true;
                                break;
                            }
                        }
                        if (status === true) {
                            user.roles[$scope.roleList[i].Id] = true;
                        }
                    }
                    $scope.user = user;
                    console.log($scope.user);
                }
            });
            $scope.$watch('roleList', function(roleList){
                if (roleList !== undefined) {
                    $scope.roleList = roleList;
                }
            });
        };

        $scope.loadUser = function(userId) {
            $scope.user = UserDetailLoader(userId);
            $scope.enabled = true;
            $('#overview-button').tab('show');
        };

        $scope.unloadUser = function() {
            $scope.$parent.selectedUserId = null;
            $scope.user = undefined;
            $scope.enabled = false;
        };

        $scope.saveUser = function() {
            var user = {};
            if ($scope.user !== undefined) {
                //user.Id = $scope.user.Id;
                user = $scope.user;
            }
            
            /*
            // should be without jquery, but angular has some problems with contenteditable
            // and there is a directive to solve this problem, but it's causing more problems.
            // this should be changed.
            user.FirstName = $('#userFirstName').html();
            user.LastName = $('#userLastName').html();
            user.Name = $('#userName').html();
            user.EMail = $('#userEmail').html();
            user.PhoneNumber = $('#userPhone').html();
            user.Address = $('#userAddress').html();

            for (var i in user) {
                if (user[i] === '') {
                    delete user[i];
                }
            }
            */

            if (user.Id === undefined) {
                user.Password = (new sha($('#userPassword').html(), 'ASCII')).getHash('SHA-512', 'HEX');
                var result = User.save(user);
                user.Id = result.Id;
            } else {
                User.update(user);
                user.Password = $('#userPassword').html();
                if (user.Password !== '') {
                    user.Password = (new sha($('#userPassword').html(), 'ASCII')).getHash('SHA-512', 'HEX');
                    User.update({Id: user.Id, Action: 'Password', NewPassword: user.Password});
                }
                User.delete({Id: user.Id, Action: 'Role'});
            }

            if ($scope.user !== undefined) {
                for (var i in $scope.user.roles) {
                    if ($scope.user.roles[i] === true) {
                        User.update({Id: user.Id, Action: 'Role', Action2: i});
                    }
                }
            } else {
                for (var i in $scope.newUser.roles) {
                    if ($scope.newUser.roles[i] === true) {
                        User.update({Id: user.Id, Action: 'Role', Action2: i});
                    }
                }
            }

            $scope.$parent.loadUsers();
            $scope.unloadUser();
        }

        //
        $scope.initialize();

    };
});
