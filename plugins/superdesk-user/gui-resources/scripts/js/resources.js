define([
    'angular',
    'angular-resource'
],function(angular) {
    'use strict';

    var resources = angular.module('users.resources', ['ngResource']);

    resources.factory('User', ['$resource', '$q', function($resource, $q) {
        return $resource('/resources/HR/User/:Id/:Action', {Id: '@Id', Action: '@Action'}, {
            query: {method: 'GET', params: {'X-Filter': '*'}},
            update: {method: 'PUT'},
            save: {method: 'POST', params: {'X-Filter': 'Id'}}
        });
    }]);

    resources.factory('UserListLoader', ['User', '$q', function(User, $q) {
        return function(offset, limit, searchTerm) {
            var delay = $q.defer();
            var parameters = {offset: offset, limit: limit};
            if (searchTerm !== undefined && searchTerm !== '') {
                parameters['all.ilike'] = searchTerm;
            }
            User.query(parameters, function(response) {
                for (var i = 0; i < response.UserList.length; i = i + 1) {
                    response.UserList[i].checked = false;
                }
                response.UserList.count = response.total;
                delay.resolve(response.UserList);
            });
            return delay.promise;
        };
    }]);

    resources.service('UserService', ['$resource', '$q', function($resource, $q) {
        var UserImage = $resource('/resources/HR/Person/:userId/MetaData/Icon', {userId: '@userId'});

        this.getImage = function(user) {
            var delay = $q.defer();

            UserImage.get({userId: user.Id}, function(image) {
                delay.resolve(image);
            }, function() {
                delay.reject();
            });

            return delay.promise;
        };
    }]);
});
