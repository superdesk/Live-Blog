define([
    'jquery',
	'angular',
    config.guiJs('livedesk', 'authorization'),
    'interceptor'
	],function($, angular, auth, interceptor){
        var angularHeaders = $.extend({}, auth, { 'Content-Type': 'text/json' });
		var feeds = angular.module('manageFeeds',[]);
        feeds.config(['$interpolateProvider', function($interpolateProvider) {
            $interpolateProvider.startSymbol('{{ ');
            $interpolateProvider.endSymbol(' }}');
        }]);
        feeds.run(function($http){
            var authObject = {
                'Authorization': localStorage.getItem('superdesk.login.session')
            }
            var angularHeaders = $.extend({}, authObject, { 'Content-Type': 'text/json' });
            $http.defaults.headers.get = authObject;
            $http.defaults.headers.post = angularHeaders;
            $http.defaults.headers.put = angularHeaders;
            $http.defaults.headers.delete = authObject;
        });
        feeds.config(function($httpProvider){
		    delete $httpProvider.defaults.headers.common['X-Requested-With'];
            $httpProvider.interceptors.push(interceptor);
		});
        return feeds;
});