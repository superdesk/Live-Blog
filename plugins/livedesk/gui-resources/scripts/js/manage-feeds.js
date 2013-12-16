define([
    'jquery',
    'gizmo/superdesk',
    'livedesk/views/provider-edit',
    'angular',
    'lib/livedesk/scripts/js/manage-feeds/manage-feeds',
    'lib/livedesk/scripts/js/manage-feeds/services/chained-blogs-data',
    'lib/livedesk/scripts/js/manage-feeds/services/add-provider',
    'lib/livedesk/scripts/js/manage-feeds/services/sms-data',
    'lib/livedesk/scripts/js/manage-feeds/directives/checkbox-custom',
    'lib/livedesk/scripts/js/manage-feeds/directives/sms-checkbox-custom',
    'tmpl!livedesk>layouts/livedesk',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!livedesk>manage-feeds',
    'tmpl!livedesk>manage-feeds-provider',
    'tmpl!livedesk>manage-feeds-external-blog',
], function ($, Gizmo, EditProviderView, ngular, feeds) {
    function getGizmoUrl(path) {
        var url = new Gizmo.Url(path);
        return url.get();
    }

    function getLastId(blogHref) {
        //small hack to get the blog id
        //@TODO get it in a smarter way
        var hackArray = blogHref.split('/');
        var blogId = hackArray[hackArray.length - 1];
        return blogId;
    }

    return function(blogHref) {
        var SMS_TYPE = 'smsblog';
        var PROVIDER_TYPE = 'blog provider';
        var blogId = getLastId(blogHref);

        var sourcesUrl = getGizmoUrl('LiveDesk/Blog/' + blogId + '/Source') + '?X-Filter=*';
        var smsUrl = getGizmoUrl('Data/SourceType/smsfeed/Source') + '?X-Filter=Name,Id';
        var smsSourcesUrl = getGizmoUrl('Data/SourceType/smsblog/Source?blogId=' + blogId + '&X-Filter=*') ;

        var providersUrl = getGizmoUrl('Data/SourceType/' + PROVIDER_TYPE + '/Source') + '?X-Filter=Name,Id,URI';
        var chainBlogUrl = getGizmoUrl('LiveDesk/Blog/' + blogId + '/Source');
  

        feeds.controller('chainedBlogs', function($scope, $http, chainedBlogsData, provider, smsData) {
            //initializing some vars
            $scope.chains = [];
            $scope.newTitle = '';
            $scope.newUrl = '';

            $scope.msg = {
                newTitleError: false,
                newUrlError: false,
                newInputError: false,
                noChains: true,
                noSmsFeeds: true
            };

            $scope.smss = [];
            $scope.handleChange = function(sms) {
                if ( sms.assigned ) {
                    assign(sms);
                } else {
                    unassign(sms);
                }
            };

            var checkChains = function() {
                $scope.msg.noChains = $scope.chains.length === 0;
            };

            var assign = function(sms) {
                var name = sms.Name;
                var newSource = {
                    Name: name,
                    Type: SMS_TYPE,
                    IsModifiable: 'True',
                    URI: name
                };
                var assignUrl = getGizmoUrl('LiveDesk/Blog/' + blogId + '/Source');
                $http.post(assignUrl, newSource);
            };

            var unassign = function(sms) {
                var unassignUrl = getGizmoUrl('LiveDesk/Blog/' + blogId + '/Source/' + sms.source);
                $http({method: 'DELETE', url: unassignUrl});
            };

            //get the sms feeds
            smsData.getData(smsUrl, smsSourcesUrl).then(function(data){
                $scope.smss = data;
                $scope.msg.noSmsFeeds = $scope.smss.length === 0;
            });

            //done here with sms starting with chained blogs

            chainedBlogsData.getData(providersUrl, sourcesUrl).then(function(chains){
                $scope.chains = chains;
                checkChains();
            });
            
            var isUrl = function(url) {
                return url && url.match(/^(https?:)?\/\//);
            };

            $scope.chainChange = function (blog, OriginUri, parentIndex, index) {
                if ( blog.chained ) {
                    //add source
                    var name = blog.Title;
                    var URI = blog.href;
                    var newChainedBlog = {
                        'IsModifiable': 'True',
                        'Name': name,
                        'OriginURI': OriginUri,
                        'Type': 'chained blog',
                        'URI': URI
                    }
                    $http.post(chainBlogUrl, newChainedBlog).
                    success(function(data, status, headers, config) {
                        var sourceId = getLastId(data.href);
                        $scope.chains[parentIndex].blogList[index].sourceId = sourceId;
                        $scope.chains[parentIndex].blogList[index].chained = true;
                    });
                } else {
                    var unchainUrl = getGizmoUrl('LiveDesk/Blog/' + blogId + '/Source/' + blog.sourceId);
                    $http({method: 'DELETE', url: unchainUrl});
                    $scope.chains[parentIndex].blogList[index].chained = false;

                }
            };

            $scope.removeProvider = function (chain) {
                var index = $scope.chains.indexOf( chain );
                if ( confirm(_("Removing provider will unchain its blogs.\nAre you sure to continue?")) ){
                    var removeSourceUrl = getGizmoUrl('Data/Source/' + chain.Id);
                    provider.unchainBlogs(getGizmoUrl('LiveDesk/Blog/' + blogId + '/Source/'), chain.blogList);
                    $http({method: 'DELETE', url: removeSourceUrl});
                    $scope.chains.splice(index, 1);
                    checkChains();
                }
            };

            $scope.preEditProvider = function(provider) {
                if ( typeof provider == "undefined" ) {
                    $scope.provider = -1;
                } else {
                    $scope.provider = provider;
                    $scope.newTitle = provider.Name;
                    $scope.newUrl = provider.URI.href;
                }
            };

            var cleanEditForm = function() {
                $scope.newTitle = '';
                $scope.newUrl = '';
                //$scope.provider = -1;
                jQuery('#AddProvider').modal('hide');
            };

            $scope.editProvider = function() {
                var valid = true;
                if ( $scope.newTitle.length < 1 ) {
                    $scope.msg.newTitleError = true;
                    valid = false;
                } else {
                    $scope.msg.newTitleError = false;
                }
                if ( !isUrl($scope.newUrl) ) {
                    $scope.msg.newUrlError = true;
                    valid = false;
                } else {
                    $scope.msg.newUrlError = false;
                }

                if ( valid ) {
                     var myData = {
                        'IsModifiable': "True",
                        'Name': $scope.newTitle,
                        'Type': PROVIDER_TYPE,
                        'URI': $scope.newUrl
                    };

                    if ( $scope.provider == -1 ) {
                        provider.addData(getGizmoUrl('Data/Source'), myData).then(function(data){
                            provider.createProviderObject(data).then(function(data){
                                $scope.chains.push(data);
                                cleanEditForm();
                                checkChains();
                            }, function(data){
                                $scope.msg.newInputError = true;
                            })
                        }, function(data) {
                            $scope.msg.newInputError = true;
                        }); 
                    } else {

                        //get the new blogs
                        if ( $scope.provider.URI.href != $scope.newUrl ) {
                            //unchain the existing blogs
                            provider.unchainBlogs(getGizmoUrl('LiveDesk/Blog/' + blogId + '/Source/'), $scope.provider.blogList);
                            provider.getBlogs($scope.newUrl).then(function(data){
                                $scope.provider.blogList = data;
                            });
                            $scope.provider.URI.href = $scope.newUrl;
                        }
                        $scope.provider.Name = $scope.newTitle;
                        cleanEditForm();

                        //this is commented out because the PUT problem that Gabriel has to fix
                        /*
                        provider.editProvider(getGizmoUrl('Data/Source/' + $scope.provider.Id), {Name: $scope.newTitle, URI: $scope.newUrl}).then(function(data){
                            console.log('the PUT request succeded');
                            //change the object
                        }, function(data) {
                            console.log('error ON PUT ', data);
                            $scope.newInputError = true;
                        });
*/
                        
                    }
                }
            };
        });

        var myBlog = Gizmo.Auth(new Gizmo.Register.Blog(blogHref));
        myBlog.sync().done(function(data){
            var myData = {
                Title: data.Title, 
                Id: data.Id,
                ui: {
                    content: 'is-content=1', 
                    submenu: 'is-submenu', 
                    submenuActive4: 'active'    
                }
            }
            $('#area-main').tmpl( 'livedesk>manage-feeds', myData );
            $('#controller-heaven').attr('ng-controller', 'chainedBlogs');
            angular.bootstrap(document, ['manageFeeds']);        
        });
    }
});
