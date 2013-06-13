define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, ArticleListLoader) {
        $('body').removeClass().addClass('article-list'); //

        $scope.articles = ArticleListLoader();
        
        $q.when($scope.articles).then(function(articles){
            console.log(articles);
        });
    };
});
