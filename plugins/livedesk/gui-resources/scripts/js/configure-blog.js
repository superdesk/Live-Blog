define([ 
    'jquery',
    'jquery/rest', 'jqueryui/texteditor', 'jquery/avatar',
         'tmpl!livedesk>layouts/livedesk', 'tmpl!livedesk>layouts/blog', 
         'tmpl!livedesk>configure', 'tmpl!livedesk>configure/internal-colabs' ],
function($)
{
    var content = null,
    blogHref = null,
    blogData = null,
    aedit =
    {
        _create: function(elements)
        {
            $(elements).on('focusout.livedesk click.livedesk', function()
            {
                $(this).attr('href', $(this).text());
            });
        }
    },
    saveBlog = function()
    {
        var data = { OutputLink: content.find('[data-key="OutputLink"]').text() };
        var langVal = $.trim(content.find('[data-key="Language"]:eq(0)').val());
        if( langVal !== '' ) data.Language = langVal; 
        new $.restAuth(blogHref).update(data).done(function(data)
        {
            
            $('[is-submenu] .alert')
                .removeClass('alert-error hide')
                .addClass('alert-success').find('span').text(_('Configuration updated'));
        })
        .fail(function(data)
        { 
            $('[is-submenu] .alert')
                .removeClass('alert-success hide')
                .addClass('alert-error').find('span').text(_('Error'));
        });
    },
    init = function()
    {
        content = $('[is-content]');
        content.find('[data-key="OutputLink"]').texteditor({plugins: {toolbar: null, aedit: aedit}});
        
        // language select
        new $.rest('Superdesk/Language').xfilter('Id,Name').done(function(Languages)
        {
            var html = '<option value="">'+_('Choose language')+'</option>',
                langInput = content.find('[data-key="Language"]');
            for( var i in Languages )
                html += '<option value="'+Languages[i].Id+'">'+Languages[i].Name+'</option>';
            langInput.html(html).val(langInput.attr('data-value'));
        });
        
        var topSubMenu = $(this).find('[is-submenu]');
        $(topSubMenu)
        .off('click.livedesk', 'a[data-target="configure-blog"]')
        .on('click.livedesk', 'a[data-target="configure-blog"]', function(event)
        {
            event.preventDefault();
            var blogHref = $(this).attr('href')
            $.superdesk.getActions('modules.livedesk.configure')
            .done(function(action)
            {
                action.ScriptPath &&
                    require([$.superdesk.apiUrl+action.ScriptPath], function(app){ new app(blogHref); });
            });
        })
        .off('click.livedesk', 'a[data-target="edit-blog"]')
        .on('click.livedesk', 'a[data-target="edit-blog"]', function(event)
        {
            event.preventDefault();
            var blogHref = $(this).attr('href');
            $.superdesk.getAction('modules.livedesk.edit')
            .done(function(action)
            {
                action.ScriptPath && 
					require([$.superdesk.apiUrl+action.ScriptPath], function(EditApp){ EditApp(blogHref); });
            });
        })
        .off('click.livedesk', 'a[data-target="manage-collaborators-blog"]')
        .on('click.livedesk', 'a[data-target="manage-collaborators-blog"]', function(event)
        {
            event.preventDefault();
            var blogHref = $(this).attr('href')
            $.superdesk.getAction('modules.livedesk.manage-collaborators')
            .done(function(action)
            {
                action.ScriptPath && 
                    require([$.superdesk.apiUrl+action.ScriptPath], function(app){ new app(blogHref); });
            });
        });
        $('[data-action="save"]', content)
            .off('click.livedesk')
            .on('click.livedesk', function(){ saveBlog(); saveColabs(); });
        $('[data-action="save-close"]', content)
            .off('click.livedesk')
            .on('click.livedesk', function(){ $.when(saveBlog(), saveColabs()).then(function(){ $('a[data-target="edit-blog"]').click(); }); });
        $('[data-action="cancel"]', content)
            .off('click.livedesk')
            .on('click.livedesk', function(){ $('a[data-target="edit-blog"]').click(); });
    },
    app = function(theBlog)
    {
        blogHref = theBlog;
		var EmbedPath = config.content_url+'/'+config.guiJs('livedesk','embed/')
			EmbedSource = '<ul id="livedesk-root"><li>Loading...</li></ul><'+'script>var link=document.createElement("link");link.rel="stylesheet";link.type="text/css";link.href="'+EmbedPath+'live-blog.css";document.getElementsByTagName("head")[0].appendChild(link);window.livedesk = { callback: function(){ new this.TimelineView({ url: "'+blogHref+'" });}, productionServer: "localhost:8080", frontendServer: function(){ return "localhost:8080";}, contentPath: "'+EmbedPath+'"};';
			EmbedSource += '(function(d, s, id){var js, fjs = d.getElementsByTagName(s)[0];if (d.getElementById(id)) return;js = d.createElement(s); js.id = id;js.src = "'+EmbedPath+'/livedeskembed.js";fjs.parentNode.insertBefore(js, fjs);}(document, "script", "livedesk-jssdk"));<'+'/script>';
        gotColabs = new $.Deferred;
		new $.restAuth(theBlog).xfilter('Creator.Name, Creator.Id').done(function(data)
        {
            blogData = data;
            var data = $.extend({}, data, {
					BlogHref: theBlog, 
                    ui: {
						content: 'is-content=1', 
						side: 'is-side=1', 
						submenu: 'is-submenu', 
						submenuActive2: 'active'
						
					},
					EmbedSource: EmbedSource
					}),
                content = $.superdesk.applyLayout('livedesk>configure', data, init);
				$('.controls textarea').focus(function() { $(this).select(); } );
        });
    };
    return app;
});