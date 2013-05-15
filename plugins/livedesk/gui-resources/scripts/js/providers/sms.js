define([
	'providers',
	'jquery',
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/sms/adaptor',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>providers/sms',
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/sources/sms',
    'tmpl!livedesk>items/implementors/sources/base',
    'tmpl!livedesk>items/implementors/sources/sms',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/loading'
], function( providers, $, Gizmo, BlogAction) {
$.extend(providers.sms, {
    interval: 30000,
    first: true,
    oldSmss: [],
    data: [],
	init: function(){
        this.adaptor.init();
        this.render();
	},
    render: function(){
        var self = this;
        this.el.tmpl('livedesk>providers/sms', {}, function(){
            self.getAllSmss();
            var int = setInterval(function(){
                self.getAllSmss();
            }, self.interval);
        });
    },
    getAllSmss: function() {
        var self = this;
        var url = new Gizmo.Url('Data/SourceType/FrontlineSMS/Post');
        myUrl = url.get() + '?X-Filter=Content,Id,CreatedOn,Creator.*';
        self.data.sms = [];
        var cleanUrl = 'http:' + url.get();
        $.ajax({
            url: myUrl
        }).done(function(data){
            var smss = data.PostList;
            smss = smss;

            if ( self.first ) {
                self.oldSmss = smss;
                self.first = false;
            } else {
                if ( self.oldSmss == smss ) {
                    //don't refresh the whole thing
                    return;
                } else {
                    self.oldSmss = smss;
                }
            }
            //clean the results
            $('#sms-search-results').html('');
            smss.reverse();
            //prepare the data for dragging to timeline
            posts = [];
            for ( var i = 0; i < smss.length; i++ ) {
                var item = smss[i];
                item['message'] = item.Content;
                posts.push({ Meta: item });
                self.data.sms[item.Id] = item;
            }
            if ( posts.length > 0 ) {
                $.tmpl('livedesk>items/item', {
                    Post: posts,
                    Base: 'implementors/sources/sms',
                    Item: 'sources/sms'
                }, function(e, o) {
                    el = $('#sms-search-results').append(o).find('.smspost');
                    BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                        el.draggable(
                        {
                            revert: 'invalid',
                            containment:'document',
                            helper: 'clone',
                            appendTo: 'body',
                            zIndex: 2700,
                            clone: true,
                            start: function(evt, ui) {
                                item = $(evt.currentTarget);
                                $(ui.helper).css('width', item.width());
                                var itemNo = $(this).attr('data-id');
                                var elData = self.adaptor.universal(self.data.sms[ itemNo ]);
                                $(this).data('data', self.adaptor.universal(self.data.sms[ itemNo ]));
                            }
                        });
                    }).fail(function(){
                        el.removeClass('draggable').css('cursor','');
                    });
                }); 
            } else {
                $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                    $('#sms-search-results').append(o);
                });
            }
        });
    }
});
return providers;
});