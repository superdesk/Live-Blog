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
            $httpProvider.defaults.headers.get = { 'Authorization': localStorage.getItem('superdesk.login.session') }
            $httpProvider.defaults.headers.post = { 'Authorization': localStorage.getItem('superdesk.login.session') }
		});
        return feeds;
});