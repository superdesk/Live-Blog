define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, Article, ArticleListLoader) {
        
        $scope.initialize = function() {
            $('body').removeClass().addClass('article-list'); // hack, should be removed after templates are fixed
            
            $scope.loadSettings();

            $scope.pageMax = 1;
            $scope.page = 1;

            $scope.allChecked = false;

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
                    if ($scope.pageMax === 0) {
                        $scope.pageMax = 1;
                    }
                    delete articles.count;
                    $scope.articles = articles;
                }
            });
            $scope.$watch('searchTerm', function(searchTerm){
                if (searchTerm === undefined) {
                    searchTerm = '';
                }
                $scope.loadArticles();
            });

            $('.sf-checkbox').each(function(i,val){
                var ischecked = "";
                if ($(val).attr("checked")=="checked") ischecked="sf-checked";
                $(val).wrap('<span class="sf-checkbox-custom ' + ischecked + '"></span>');
                $(val).hide();

                var set_bg = $(val).attr("set-bg"); 
                if (typeof set_bg !== undefined && set_bg !== false && $(val).attr("checked")=="checked") {
                    $(this).parents().eq(set_bg).toggleClass('active-bg');
                }
            });

            $('.sf-checkbox-custom').click(function(e){
                e.preventDefault();
                $(this).toggleClass('sf-checked');
                var own_box = $(this).find(".sf-checkbox").first();
                //set active class

                var set_bg = own_box.attr("set-bg"); 
                if (typeof set_bg !== undefined && set_bg !== false) {
                    $(this).parents().eq(set_bg-1).toggleClass('active-bg');
                }

                if (own_box.prop('checked')==true) {
                    own_box.prop('checked',false);
                } else {
                    own_box.prop('checked',true);
                }
                return false;
            });
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
                $scope.newArticleTitle = '';
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
        $scope.toggle = function(index) {
            if ($scope.articles[index].checked === false) {
                $scope.allChecked = false;
            } else {
                var allChecked = true;
                for (var i = 0; i < $scope.articles.length; i = i + 1) {
                    if ($scope.articles[i].checked === false) {
                        allChecked = false;
                    }
                }
                $scope.allChecked = allChecked;
            }
        };
        $scope.toggleAll = function() {
            for (var i = 0; i < $scope.articles.length; i = i + 1) {
                $scope.articles[i].checked = $scope.allChecked;
            }
        };
        $scope.publishArticles = function() {
            for (var i = 0; i < $scope.articles.length; i = i + 1) {
                if ($scope.articles[i].checked === true) {
                    $scope.publishArticle($scope.articles[i].Id);
                }
            }
        };
        $scope.unpublishArticles = function() {
            for (var i = 0; i < $scope.articles.length; i = i + 1) {
                if ($scope.articles[i].checked === true) {
                    $scope.unpublishArticle($scope.articles[i].Id);
                }
            }
        };
        $scope.deleteArticles = function() {
            for (var i = 0; i < $scope.articles.length; i = i + 1) {
                if ($scope.articles[i].checked === true) {
                    $scope.deleteArticle($scope.articles[i].Id);
                }
            }
        };

        //

        $scope.initialize();

    };
});
