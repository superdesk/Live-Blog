define([
	'angular',
	],function(){
		var feeds = angular.module('manageFeeds',[]);
        feeds.config(['$interpolateProvider', function($interpolateProvider) {
            $interpolateProvider.startSymbol('{{ ');
            $interpolateProvider.endSymbol(' }}');
        }]);
        feeds.config(function($httpProvider){
		    delete $httpProvider.defaults.headers.common['X-Requested-With'];
		});
        return feeds;
});