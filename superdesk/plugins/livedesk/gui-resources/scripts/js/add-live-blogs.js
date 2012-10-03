define([
	'providers/enabled',
	'jquery', 'jquery/superdesk', 'jquery/rest', 'jqueryui/texteditor', 'jquery/utils',
	'tmpl!livedesk>add'
], function(providers, $, superdesk) {

    var hasEditor = false;
    initAddBlog = function()
    {
        var initDialog = function()
        {
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
            $(this).find("h2[data-value='Title']").texteditor
            ({
                plugins: {controls: h2ctrl},
                floatingToolbar: 'top'
            }) && 
            $(this).find("article[data-value='Description']")
                .texteditor({floatingToolbar: 'top', plugins:{ controls: editorTitleControls }});
            hasEditor = true;
        };
        
        $('#add-live-blog')
        .dialog
        ({
            draggable: false,
            resizable: false,
            modal: true,
            width: "40.1709%",
            autoOpen: true,
            open: initDialog,
            buttons: 
            [
                 { text: "Save", click: function(){ $(this).find('form').trigger('submit'); }, class: "btn btn-primary"},
                 { text: "Close", click: function(){ $(this).dialog('close'); }, class: "btn"}
            ]
        });
    
        $('#add-live-blog form')
            .off('submit.livedesk')
            .on('submit.livedesk', function(e)
            {
                e.preventDefault();
                var lang = $("#add-live-blog [name='Language']:eq(0)"),
                    title = $("#add-live-blog [data-value='Title']:eq(0)"),
                    descr = $("#add-live-blog [data-value='Description']:eq(0)");
                if( lang.val() == '' )
                {
                    lang.parents('.control-group:eq(0)').addClass('error');
                    lang.trigger('focus');
                    return;
                }
                var data = 
                {
                    Language: $("#add-live-blog [name='Language']:eq(0)").val(),
                    Title: $.styledNodeHtml(title).replace(/<br\s*\/?>\s*$/, ''),
					Type: '1',
                    Description: $.styledNodeHtml(descr).replace(/<br\s*\/?>\s*$/, '')
                };
                new $.restAuth('LiveDesk/Blog').insert(data).done(function(liveBlog)
                {
                    $("#add-live-blog")
                        .dialog('close')
                        .find("[name='Language']:eq(0)").val('')
                            .parents('.control-group').removeClass('error').end().end()
                        .find("[data-value='Title']:eq(0)").html('').end()
                        .find("[data-value='Description']:eq(0)").html('');

                    require([$.superdesk.apiUrl+'/content/lib/livedesk/scripts/js/edit-live-blogs.js'],
                        function(EditApp){
                            new EditApp(liveBlog.href);
                            $('#navbar-top').trigger('refresh-menu');
                        });
                });
            });
        
    },
    AddApp = function()
    {
        var el = $('#add-live-blog');
        if(!el.length) {
            new $.rest('Superdesk/Language').xfilter('Id,Name').done(function(Languages){
                $.tmpl('livedesk>add', {ui: {content: 'is-content=1'}, Languages: Languages }, function(e,o){
                    $('#area-main').append(o);
                    initAddBlog();
                });
            });
        } else {
            initAddBlog();
        }
        
        superdesk.hideLoader();
    };
    return AddApp;
});