 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/languages'),
    config.guiJs('livedesk', 'views/blogtypes'),
    config.guiJs('livedesk', 'models/blog'),
   'jquery/superdesk',
   'jqueryui/texteditor',
    'tmpl!livedesk>add' 
], function( $, Gizmo, LanguagesView, BlogTypesView) {
   var hasEditor = false;
   return Gizmo.View.extend({
        events: {
            '.save': { 'click': 'save' }
        },
        init: function() {
            if(!this.model) {
                this.model = Gizmo.Auth(new Gizmo.Register.Blog());
            }
        },
        refresh: function() {
            var self = this;
            $.tmpl('livedesk>add', {}, function(e, o){
                self.setElement(o);
                self.languagesView = new LanguagesView({
                    el: self.el.find('.languages'),
                    _parent: self
                });
                self.blogtypesView = new BlogTypesView({
                    el: self.el.find('.blogtypes'),
                    tmplData: { add: true },
                    _parent: self
                });
                var h2ctrl = $.extend({}, $.ui.texteditor.prototype.plugins.controls),
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
                    editorTitleControls = $.extend({}, $.ui.texteditor.prototype.plugins.controls, { image : editorImageControl });
                    
                delete h2ctrl.justifyRight;
                delete h2ctrl.justifyLeft;
                delete h2ctrl.justifyCenter; 
                delete h2ctrl.html;
                delete h2ctrl.image;
                delete h2ctrl.link;
                !hasEditor && 
                self.el.find("h2[data-value='Title']").texteditor
                ({
                    plugins: {controls: h2ctrl},
                    floatingToolbar: 'top'
                }) && 
                self.el.find("article[data-value='Description']")
                    .texteditor({floatingToolbar: 'top', plugins:{ controls: editorTitleControls }});
                hasEditor = true; 
                self.el.modal('show');
            });
        },
        save: function(event) {
            event.preventDefault();
            var 
                self = this,
                lang = self.el.find("[name='Language']:eq(0)"),
                title = self.el.find("[data-value='Title']:eq(0)"),
                blogtypeControl = self.el.find("[name='blogtypeselection']"),
                blogtype = self.el.find("[name='blogtypeselection']:checked"),
                descr = self.el.find("[data-value='Description']:eq(0)");
            if( lang.val() == '' )
            {
                lang.parents('.control-group:eq(0)').addClass('error');
                lang.trigger('focus');
                return;
            } else {
                lang.parents('.control-group:eq(0)').removeClass('error');
            }
            if( blogtype.val() === undefined )
            {
                blogtypeControl.parents('.control-group:eq(0)').addClass('error');
                blogtypeControl.first().trigger('focus');
                return;
            } else {
                blogtypeControl.parents('.control-group:eq(0)').removeClass('error');
            }
            var 
                data = 
                {
                    Language: lang.val(),
                    Title: $.styledNodeHtml(title).replace(/<br\s*\/?>\s*$/, ''),
                    Type: blogtype.val(),
                    Description: $.styledNodeHtml(descr).replace(/<br\s*\/?>\s*$/, ''),
                    Creator: localStorage.getItem('superdesk.login.id')
                };
            self.model.set(data).xfilter('Id,Description,Title,CreatedOn,Creator.*,Language,Type,Admin').sync().done(function(liveBlog){
                    require([$.superdesk.apiUrl+'/content/lib/livedesk/scripts/js/edit-live-blogs.js'],
                        function(EditApp){
                            $.superdesk.navigation.bind( 'live-blog/'+liveBlog.Id, 
                                    function(){ 
                                        new EditApp(liveBlog.href); 
                                        $('#navbar-top').trigger('refresh-menu');
                                    }, 
                                    liveBlog.Title );
                        });
             });
        }
    });
});