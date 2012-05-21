define([
	'providers/enabled',
	'jquery', 'jquery/rest', 'jquery/superdesk',
	'tmpl!livedesk>add'
], function(providers, $) {

    var
    initAddBlog = function(){
        $('#add-live-blog')
            .modal()
            .on('click','[ci="save"]',function(e){
                var data = {};
                $('#add-live-blog').find('[name]').each(function(){
                    var el = $(this);
                    data[el.attr('name')]= el.val();
                });
                new $.restAuth('LiveDesk/Blog').insert(data).done(function(){
                    console.dir(arguments);
                    require([superdesk.apiUrl+'/content/gui/superdesk/livedesk/scripts/js/edit-live-blogs.js'],
                        function(EditApp){ new EditApp(theBlog); });
                });
                //console.log(data);
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
    };
    return AddApp;
});