define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, Article, ArticleListLoader) {
        
        $scope.initialize = function() {
            $('body').removeClass().addClass('article-list'); // hack, should be removed after templates are fixed
            
            $scope.loadSettings();

            $scope.$watch('page', function(page) {
                $scope.loadArticles();
            });
            $scope.$watch('settings', function(settings, oldSettings) {
                $scope.saveSettings();
                if (settings.itemsPerPage !== oldSettings.itemsPerPage) {
                    $scope.loadArticles();
                }
            }, true);
            $scope.$watch('articles', function(articles){
                if (articles !== undefined) {
                    $scope.pageMax = Math.ceil(articles.count / $scope.settings.itemsPerPage);
                }
            });
            $scope.$watch('searchTerm', function(searchTerm){
                if (searchTerm === undefined) {
                    searchTerm = '';
                }
                $scope.loadArticles();
            });

            $scope.pageMax = 1;
            $scope.page = 1;
        };
        $scope.saveSettings = function() {
            localStorage.setItem('superdesk.articleList.settings', angular.toJson($scope.settings));
        };
        $scope.loadSettings = function() {
            $scope.settings = angular.fromJson(localStorage.getItem('superdesk.articleList.settings'));
            if ($scope.settings === null) {
                $scope.settings = {
                    itemsPerPage: 25,
                    viewType: 'list',
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
            }
        };
        $scope.createArticle = function() {
            var content = {Title: $scope.newArticleTitle, Lead: '', Body: ''};
            Article.save({
                Content: angular.toJson(content),
                Creator: localStorage.getItem('superdesk.login.id'),
                Author: localStorage.getItem('superdesk.login.id')
            }, function(){
                $scope.loadArticles();
            });
        };
        $scope.deleteArticle = function(articleId) {
            Article.delete({Id: articleId}, function(){
                $scope.loadArticles();
            });
        };
        $scope.publishArticle = function(articleId) {
            Article.update({Id: articleId, Action: 'Publish'}, function(){
                $scope.loadArticles();
            });
        };
        $scope.unpublishArticle = function(articleId) {
            Article.update({Id: articleId, Action: 'Unpublish'}, function(){
                $scope.loadArticles();
            });
        };
        $scope.loadArticles = function() {
            var limit = $scope.settings.itemsPerPage;
            var offset = ($scope.page - 1) * limit;

            $scope.articles = ArticleListLoader(offset, limit, $scope.searchTerm);
        };

        //

        $scope.initialize();

    };
});
