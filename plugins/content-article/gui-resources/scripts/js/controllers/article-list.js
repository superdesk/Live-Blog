define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, ArticleListLoader) {
        $scope.saveSettings = function() {
            localStorage.setItem('superdesk.articleList.settings', angular.toJson($scope.settings));
        };
        $scope.loadSettings = function() {
            $scope.settings = angular.fromJson(localStorage.getItem('superdesk.articleList.settings'));
            if ($scope.settings === null) {
                $scope.settings = {
                    itemsPerPage: 25,
                    viewType: 'grid',
                    fields: {
                        title: true,
                        author: true,
                        publishDate: true,
                        status: true,
                        readCount: false,
                        importance: false,
                        collaborators: false,
                        action: true
                    }
                };
                $scope.saveSettings();
            }
        };

        //

        $('body').removeClass().addClass('article-list'); // hack, should be removed after templates are fixed
        $scope.loadSettings();

        $scope.articles = ArticleListLoader();
        
        $q.when($scope.articles).then(function(articles){
            for (var i = 0; i < articles.length; i = i + 1) {
                articles[i].Content = angular.fromJson(articles[i].Content);
                if (articles[i].IsPublished === 'True') {
                    articles[i].IsPublished = true;
                } else {
                    articles[i].IsPublished = false;
                }
            }
            console.log(articles);
        });
    };
});
