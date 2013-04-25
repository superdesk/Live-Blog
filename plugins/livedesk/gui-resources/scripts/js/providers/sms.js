define([
	'providers',
	'jquery',
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/sms/adaptor',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>providers/sms',
], function( providers, $) {
$.extend(providers.sms, {
	init: function(){
        this.adaptor.init();
        this.render();
	},
    render: function(){
        var self = this;
        this.el.tmpl('livedesk>providers/sms', {}, function(){});
    }
});
return providers;
});