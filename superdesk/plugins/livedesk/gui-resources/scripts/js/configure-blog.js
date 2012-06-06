define([ 'jquery', 'jquery/rest', 'jqueryui/texteditor', 'jquery/avatar',
         'tmpl!livedesk>layouts/livedesk', 'tmpl!livedesk>layouts/blog', 
         'tmpl!livedesk>configure', 'tmpl!livedesk>configure/internal-colabs' ],
function($)
{
    var content = null,
    blogHref = null,
    blogData = null,
    currentColabIds = [],
    getColabs = function()
    {
        new $.rest('Superdesk/Collaborator')
        .xfilter('Id,Name,Person.Id,Person.FullName,Person.EMail')
        .done(function(data)
        {
            for( var i in data ) if( data[i].Person ) data[i] = $.avatar.parse(data[i]);
            $('#internal-colabs', content).tmpl('livedesk>configure/internal-colabs', {Colab: data});
        });
        new $.restAuth(blogData.Collaborator.href).xfilter('Id,Name,Person')
        .done(function(data)
        {
            $(data).each(function()
            { 
                currentColabIds.push(this.Id);
                $('#internal-colabs [data-value="Id"][value="'+this.Id+'"]', content).attr('checked', true); 
            });
        });
    },
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
        var data = { 
            OutputLink: content.find('[data-value="OutputLink"]').text(),
            Language: content.find('[data-value="Language"]:eq(0)').val()
        };
        new $.restAuth(blogHref).update(data).done(function(data)
        {
            console.log('saved');
        });
    },
    saveColabs = function()
    {
        var updateColabIds = [],
            deleteColabIds = [];
        $('#internal-colabs [data-value="Id"]').each(function()
        { 
            if( $(this).is(':checked') ) updateColabIds.push($(this).val()); 
        });
        $(currentColabIds).each(function()
        {
            !$.inArray(this, updateColabIds) && deleteColabIds.push(this);
        });
        console.log(deleteColabIds);
        console.log(currentColabIds);
    },
    init = function()
    {
        content = $('[is-content]');
        content.find('[data-value="OutputLink"]').texteditor({plugins: {toolbar: null, aedit: aedit}});
        
        // language select
        new $.rest('Superdesk/Language').xfilter('Id,Name').done(function(Languages)
        {
            var html = '<option>'+_('Choose language')+'</option>';
            for( var i in Languages )
                html += '<option value="'+Languages[i].Id+'">'+Languages[i].Name+'</option>';
            content.find('[data-value="Language"]').html(html);
        });
        
        getColabs();
        
        $('[data-action="save"]', content).off('click.livedesk')
            .on('click.livedesk', function(){ saveBlog(); saveColabs(); });
    },
    app = function(theBlog)
    {
        blogHref = theBlog;
        new $.restAuth(theBlog).xfilter('Creator.Name, Creator.Id').done(function(data)
        {
            blogData = data;
            var data = $.extend({}, data, {BlogHref: theBlog, 
                    ui: {content: 'is-content=1', side: 'is-side=1', submenu: 'is-submenu', submenuActive2: 'active'}}),
                content = $.superdesk.applyLayout('livedesk>configure', data, init);
        });
    };
    return app;
});