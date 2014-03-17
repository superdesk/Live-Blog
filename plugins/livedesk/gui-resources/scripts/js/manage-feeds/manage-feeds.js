define([
    'jquery',
	'angular',
    config.guiJs('livedesk', 'authorization'),
	],function($, angular, auth){
        var angularHeaders = $.extend({}, auth, { 'Content-Type': 'text/json' });
		var feeds = angular.module('manageFeeds',[]);
        feeds.config(['$interpolateProvider', function($interpolateProvider) {
            $interpolateProvider.startSymbol('{{ ');
            $interpolateProvider.endSymbol(' }}');
        }]);
        feeds.config(function($httpProvider){
		    delete $httpProvider.defaults.headers.common['X-Requested-With'];
            $httpProvider.defaults.headers.get = auth;
            $httpProvider.defaults.headers.post = angularHeaders;
            $httpProvider.defaults.headers.delete = auth;
            $httpProvider.defaults.headers.put = angularHeaders;
		});
        return feeds;
});