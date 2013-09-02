define([
	'angular',
    'angular-resource',
	//'manage-feed/module',
	//'manage-feed/directives/checkbox-all'
	],function(){
		var feeds = angular.module('manageFeeds', ['ngResource']);
        feeds.config(['$interpolateProvider', function($interpolateProvider) {
            $interpolateProvider.startSymbol('{{ ');
            $interpolateProvider.endSymbol(' }}');
        }]);
        feeds.config(function($httpProvider){
		    delete $httpProvider.defaults.headers.common['X-Requested-With'];
		});
        return feeds;
});