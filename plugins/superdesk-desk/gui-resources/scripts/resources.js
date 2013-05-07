define([
    'angular',
    'angular-resource'
],function(angular) {
    angular.module('resources', ['ngResource']).
        factory('Desk', function($resource) {
            return $resource('/resources/Desk/Desk/:id', {},
                {query: {method: 'GET', params: {'X-Filter': 'Id,Name'}, isArray: false}}
            );
        }).
        factory('TaskList', function($resource) {
            return $resource('/resources/Desk/Desk/:deskId/Task/?X-Filter=*');
        }).
        factory('Task', function($resource) {
            return $resource('/resources/Desk/Task/:Id', {Id: '@Id'},
                {update: {method: 'PUT'}, save: {method: 'POST', params: {'X-Filter': 'Id'}}}
            );
        });
});
