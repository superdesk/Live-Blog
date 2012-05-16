requirejs.config
({
	paths: 
	{ 
		providers:'gui/superdesk/livedesk/scripts/js/providers', 
	} 
});
define([
	'providers/enabled',
	'jquery', 'jqueryui/texteditor','jquery/splitter', 
	'tmpl!livedesk>layouts/livedesk',
	'tmpl!livedesk>layouts/blog',
	'tmpl!livedesk>add'
], function(providers, $) {
	providers = $.arrayValues(providers);
    var initAddBlog = function()
    {
		$('.tabbable').on('show','a[data-toggle="tab"]', function(e) {
			var el = $(e.target);
			var idx = parseInt(el.attr('data-idx'));
			providers[idx].el = $(el.attr('href'));
			providers[idx].init();
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
			dockKey: 'Z',	// Alt-Shift-Z in FF/IE
			accessKey: 'I'	// Alt-Shift-I in FF/IE
		});	
        var content = $(this).find('[is-content]'),
            h2ctrl = $.extend({}, $.ui.texteditor.prototype.plugins.controls);
        delete h2ctrl.justifyRight;
        delete h2ctrl.justifyLeft;
        delete h2ctrl.justifyCenter; 
        content.find('section header h2').texteditor
        ({
            plugins: {controls: h2ctrl},
            floatingToolbar: 'top'
        });
        content.find('article#blog-intro').texteditor({floatingToolbar: 'top'});
    };
    
    var AddApp = function()
    {
        $('#area-main').tmpl('livedesk>add', {ui: {content: 'is-content=1'}, providers: providers}, initAddBlog);
    };
    return AddApp;
});