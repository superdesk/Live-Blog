define([
    'providers/enabled',
    'jquery', 'jquery/splitter', 'jquery/rest', 'jqueryui/droppable',
    'jqueryui/texteditor', 'jquery/utils', 'jquery/avatar',
    'tmpl!livedesk>layouts/livedesk',
    'tmpl!livedesk>layouts/blog',
    'tmpl!livedesk>edit',
    'tmpl!livedesk>edit-timeline'],
    function(providers, $)
    {
        var config = { updateInterval: 5 },
        latestPost = 0,
        providers = $.arrayValues(providers), 
        content = null,
        blogHref = null,
        editorImageControl = function()
        {
            // call super
            var command = $.ui.texteditor.prototype.plugins.controls.image.apply(this, arguments);
            // do something on insert event
            $(command).on('image-inserted.text-editor', function()
            {
                var img = $(this.lib.selectionHas('img'));
                if( !img.parents('figure.blog-image:eq(0)').length )
                    img.wrap('<figure class="blog-image" />');
            });
            return command;
        },
        editorTitleControls = $.extend({}, $.ui.texteditor.prototype.plugins.controls, { image : editorImageControl }),
        h2ctrl = $.extend({}, $.ui.texteditor.prototype.plugins.controls),
        initEditBlog = function(theBlog)
        {
            content = $(this).find('[is-content]');
            var titleInput = content.find('section header h2'),
                descrInput = content.find('article#blog-intro'),
                editorSaveInfo = 
                {
                    _create: function(elements)
                    {
                        $(elements).on('focusout.livedesk', function()
                        {
                            if(!blogHref) return;
                            new $.rest(blogHref).update
                            ({
                                Title: $.styledNodeHtml(titleInput), 
                                Description: $.styledNodeHtml(descrInput)
                            })
                            .done(function()
                            {  
                                content.find('.tool-box-top .update-success').removeClass('hide')
                                setTimeout(function(){ content.find('.tool-box-top .update-success').addClass('hide'); }, 5000);
                            })
                            .fail(function()
                            { 
                                content.find('.tool-box-top .update-error').removeClass('hide')
                                setTimeout(function(){ content.find('.tool-box-top .update-error').addClass('hide'); }, 5000);
                            });
                        });
                    }
                };
            
            delete h2ctrl.justifyRight;
            delete h2ctrl.justifyLeft;
            delete h2ctrl.justifyCenter; 
            delete h2ctrl.html;
            delete h2ctrl.image;
            delete h2ctrl.link;
            
            titleInput.texteditor
            ({
                plugins: {controls: h2ctrl, save: editorSaveInfo},
                floatingToolbar: 'top'
            });
            descrInput.texteditor
            ({
                floatingToolbar: 'top', 
                plugins:{ save: editorSaveInfo, controls: editorTitleControls }
            });
            
            $('.tabbable')
            .on('show','a[data-toggle="tab"]', function(e)
            {
                var el = $(e.target);
                var idx = parseInt(el.attr('data-idx'));
                providers[idx].el = $(el.attr('href'));
                providers[idx].init(theBlog);
            })
            .on('hide','a[data-toggle="tab"]', function(e)
                    { console.log('cifi-cif'); })
            .find('.actived a').tab('show');
            
            $(content).on('click.livedesk', 'li.wrapup', function()
            {
                if($(this).hasClass('open'))
                    $(this).removeClass('open').addClass('closed').nextUntil('li.wrapup').hide();
                else
                    $(this).removeClass('closed').addClass('open').nextUntil('li.wrapup').show();
            }).on('click.livedesk', '.filter-posts a',function(){
                var datatype = $(this).attr('data-value');
                if(datatype == 'all') {
                    $('#timeline-view li').show();
                } else {
                    $('#timeline-view li').show();
                    $('#timeline-view li[data-post-type!="'+datatype+'"]').hide();
                }
            });
        },
        postHref = null,
        updateInterval = 0,
        updateItemCount = 0,
        updateIntervalInit = function()
        {
            if(!$('#timeline-view:visible', self.el).length) 
            {
                clearInterval(updateInterval);
                return;
            }
            update(); 
        },
        update = function(autoUpdate, callback)
        {
            new $.rest(postHref)
            .request({data:{'startEx.cId':latestPost}})
            .xfilter('Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, Creator.Id, ' +
                'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, DeletedOn')
            .done(function(posts)
            {
                if(!posts) return;

                var posts = $.avatar.parse(this.extractListData(posts), 'AuthorPerson.EMail');
                for(var i = 0; i<posts.length; i++) {
                    latestPost = Math.max(latestPost, parseInt(posts[i].CId));

                    if($.isDefined(posts[i].Creator)  && $.isDefined(posts[i].Creator.Id)
                        && (posts[i].Creator.Id == $.superdesk.login.Id)
                        && (posts[i].IsModified === "True")) {

                        posts.splice(i,1);
                        i--;
                    }
                    if($.isDefined(posts[i].DeletedOn)) {
                        $('#timeline-view .post-list li[data-post-id="'+posts[i].Id+'"]')
                            .fadeTo(500, '0.1', function(){
                                $(this).remove();
                            })
                        posts.splice(i,1);
                        i--;
                    }
                }
                updateItemCount += posts.length;
                // trigger update with callback to be applied on click
                posts.length &&
                $('#timeline-view .new-results', content).trigger('update.livedesk', [updateItemCount, function()
                {
                    $.tmpl('livedesk>edit-timeline', {Posts: posts}, function(e, o)
                    {
                        $(o).find('li').each(function(){
                            var el = $('#timeline-view .post-list li[data-post-id="'+$(this).attr('data-post-id')+'"]');
                            if($(el).length === 0) {
                                $('#timeline-view .post-list', content).prepend($(this));
                            } else {
                                $(el).replaceWith($(this).addClass('update-success'));
                                el = this;
                                setTimeout(function(){
                                    $(el).removeClass('update-success update-error');
                                }, 5000);
                            }
                        });
                        // edit posts
                        $('#timeline-view .post-list li', content)
                            .find('.editable')
                            .texteditor({plugins: {controls: h2ctrl}, floatingToolbar: 'top'})
                            .on('focusout.livedesk', function(){
                                var el = this,
                                    postId = $(el).attr('data-post-id');
                                if(!blogHref) return;
                                new $.rest(blogHref+'/Post/'+postId).update
                                    ({
                                        Content: $(el).html()
                                    })
                                    .done(function()
                                    {
                                        $(el).parents('li').addClass('update-success').removeClass('update-error');
                                        setTimeout(function(){
                                            $(el).parents('li').removeClass('update-success update-error');
                                        }, 5000);
                                    })
                                    .fail(function()
                                    {
                                        $(el).parents('li').addClass('update-error').removeClass('update-success');
                                        setTimeout(function(){
                                            $(el).parents('li').removeClass('update-success update-error');
                                        }, 5000);
                                    });
                            }).end()
                            .find('a.close').on('click.livedesk', function(){
                                var self = this,
                                    el = $(self).parents('li'),
                                    postId = $(el).attr('data-post-id');
                                $('#delete-post .yes')
                                    .off('click.livedesk')
                                    .on('click.livedesk',function(){
                                        if(!blogHref) return;
                                        new $.restAuth('Superdesk/Post/'+postId).delete().done(function(){
                                            $(el).fadeTo(500, '0.1', function(){
                                                $(this).remove();
                                            })
                                        });
                                    });
                            });
                        updateItemCount -= posts.length;
                    });
                }, autoUpdate]);
                
                callback && callback.apply(this);
            });
        };

        var EditApp = function(theBlog) {
            this.init(theBlog);
        };
        EditApp.prototype = {
            init: function(theBlog)
            {
                this.blogHref = theBlog;
                blogHref = theBlog;
            },
            update: function(){
                clearInterval(updateInterval);
                update(true, function(){ updateInterval = setInterval(updateIntervalInit, config.updateInterval*1000); });
            },
            render: function(){
                var self = this;
                new $.restAuth('Superdesk/PostType').xfilter('Key').done(function(postTypes){
                    self.prerender(postTypes);
                });
            },
            prerender: function(postTypes)
            {
                var self = this;
                new $.restAuth(this.blogHref).xfilter('Creator.Name, Creator.Id').done(function(blogData)
                {
                    var data = $.extend({}, blogData, {ui: {content: 'is-content=1', side: 'is-side=1'}, providers: providers, PostTypes: postTypes}),
                        content = $.superdesk.applyLayout('livedesk>edit', data, function(){
                            initEditBlog.call(this, self.blogHref);
                            require(['//platform.twitter.com/widgets.js'], function(){ twttr.widgets.load(); });
                        });
                    $('.live-blog-content').droppable({
                        drop: function( event, ui ) {

                            var data = ui.draggable.data('data');
                            var post = ui.draggable.data('post');
                            if(data !== undefined) {
                                new $.restAuth(self.blogHref + '/Post/Published').resetData().insert(data);
                            } else if(post !== undefined){
                                // stupid bug in jqueryui you can make draggable desstroy
                                setTimeout(function(){
                                    $(ui.draggable).removeClass('draggable').addClass('published').draggable("destroy");
                                },1);
                                new $.restAuth(self.blogHref + '/Post/'+post+'/Publish').resetData().insert();
                            }
                            // stop update interval -> update -> restart
                            self.update();
                        },
                        activeClass: 'ui-droppable-highlight',
                        accept: ':not(.edit-toolbar)'
                    });
                    $('#put-live').on('show', function(){
                        console.log('show');
                    }).on('shown', function(){
                            console.log('shown');
                        });
                    $("#MySplitter").splitter({
                        type: "v",
                        outline: true,
                        sizeLeft: 470,
                        minLeft: 470,
                        minRight: 600,
                        resizeToWidth: true,
                        //dock: "left",
                        dockSpeed: 100,
                        cookie: "docksplitter",
                        dockKey: 'Z',   // Alt-Shift-Z in FF/IE
                        accessKey: 'I'  // Alt-Shift-I in FF/IE
                    });

                    $('.collapse-title-page', content).off('click.livedesk')
                        .on('click.livedesk', function()
                        {
                            var intro = $('article#blog-intro', content);
                            !intro.is(':hidden') && intro.fadeOut('fast') && $(this).text('Expand');
                            intro.is(':hidden') && intro.fadeIn('fast') && $(this).text('Collapse');
                        });

                    postHref = blogData.PostPublished.href;
                    this.get('PostPublished')
                        .xfilter('Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
                        'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id')
                        .done(function(posts)
                        {
                            var posts = $.avatar.parse(this.extractListData(posts), 'AuthorPerson.EMail');
                            $('#timeline-view .results-placeholder', content).tmpl('livedesk>edit-timeline', {Posts: posts}, function()
                            {
                                // edit posts
                                $('#timeline-view .post-list li', content)
                                .find('.editable')
                                    .texteditor({plugins: {controls: h2ctrl}, floatingToolbar: 'top'})
                                    .on('focusout.livedesk', function(){
                                        var el = this,
                                        postId = $(el).attr('data-post-id');
                                        if(!blogHref) return;
                                        new $.rest(blogHref+'/Post/'+postId).update
                                            ({
                                                Content: $(el).html()
                                            })
                                            .done(function()
                                            {
                                                $(el).parents('li').addClass('update-success').removeClass('update-error');
                                                setTimeout(function(){
                                                    $(el).parents('li').removeClass('update-success update-error');
                                                }, 5000);
                                            })
                                            .fail(function()
                                            {
                                                $(el).parents('li').addClass('update-error').removeClass('update-success');
                                                setTimeout(function(){
                                                    $(el).parents('li').removeClass('update-success update-error');
                                                }, 5000);
                                            });
                                    }).end()
                                .find('a.close').on('click.livedesk', function(){
                                    var self = this,
                                        el = $(self).parents('li'),
                                        postId = $(el).attr('data-post-id');
                                        $('#delete-post .yes')
                                            .off('click.livedesk')
                                            .on('click.livedesk',function(){
                                                if(!blogHref) return;
                                                new $.restAuth('Superdesk/Post/'+postId).delete().done(function(){
                                                    $(el).fadeTo(500, '0.1', function(){
                                                        $(this).remove();
                                                    })
                                                });
                                            });
                                });
                                    // bind update event for new results notification button
                                $('#timeline-view .new-results', content)
                                    .off('update.livedesk')
                                    .on('update.livedesk', function(e, count, callback, autoUpdate)
                                    {
                                        var self = $(this);
                                        !autoUpdate && self.removeClass('hide').one('click.livedesk', function()
                                        {
                                            self.addClass('hide');
                                            callback.apply(self);
                                        }).find('span').text(count);
                                        autoUpdate && callback.apply(self);

                                    });
                            });

                            for(var i=0; i<posts.length; i++)
                                latestPost = Math.max(latestPost, parseInt(posts[i].CId));

                            clearInterval(updateInterval);
                            updateInterval = setInterval(updateIntervalInit, config.updateInterval*1000);

                        });
                });
                $.superdesk.hideLoader();
            }

        };
        return EditApp;
});