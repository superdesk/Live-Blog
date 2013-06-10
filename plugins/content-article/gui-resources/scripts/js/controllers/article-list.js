define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, ArticleListLoader) {
        $scope.articles = ArticleListLoader();
    };
});
