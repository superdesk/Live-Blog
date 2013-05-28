 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'models/themes'),
    'tmpl!livedesk>configure/themes',
    'tmpl!livedesk>configure/embed'
], function( $, Gizmo) {
   return Gizmo.View.extend({
        tmplData: {},
        events: {
        	'[name="Theme"]': { change: 'change'}
        },
        init: function() {
            var self = this;
            if( !self.collection ) {
                self.collection = new Gizmo.Register.Themes();
            }
            self.collection
                .on('read update', self.render, self)
                .xfilter('Name,URL')
                .sync();          
        },
        change: function(evt) {
        	var self = this,
        		el = self.el.find('[name="Theme"]'),
        		theme,
                themePath,
                themePathArray, 
                data,
                blogUrl,
                idLanguage = $('[name="Language"]').val(),
                optionLanguage = $('[name="Language"] [value="'+idLanguage+'"]');
        	if(el.val() == '') {
        		$('#emebed-script').val('');
        		return;
        	}
        	for( var i = 0, count = this.collection._list.length; i < count; i++ ){
        		theme = this.collection._list[i];
        		if(theme.get('Name') === el.val()) {
        			break;
        		}
        	}
            blogUrl = self.theBlog;
            /*!
             * If the blog url doesn't have servername in it add it
             *   else replace with the frontend server.
             */
            if(blogUrl.indexOf(config.api_url) !== -1) {
                blogUrl = blogUrl.replace(config.api_url,$('[name="FrontendServer"]').val());
            } else {
                blogUrl = $('[name="FrontendServer"]').val() + blogUrl;
            }
            themePath = theme.get('URL').href.replace('\\','/').replace(config.api_url,$('[name="FrontendServer"]').val());
            themePathArray = themePath.split('/');
            themePathArray.pop()
            themePath = themePathArray.join('/');
            data = {
                'Theme': el.val(),
                'ThemePath': themePath,
                'TheBlog': blogUrl,
                'GuiLivedeskEmbed': $('[name="FrontendServer"]').val() + '/content/' + config.guiJs('livedesk-embed','core/require.js'),
                'ApiUrl': config.api_url,
                'FrontendServer': $('[name="FrontendServer"]').val(),
                'Language': optionLanguage.attr('data-code')
            }
        	$.tmpl('livedesk>configure/embed',data, function(e,o){
        		$('#emebed-script')
        		.val(o)
        		.focus();
        	});
        },
        addOne: function(evt, model){
            //var blogTypeView = new BlogTypeView({ _parent: this, model: model, tmplData: this.tmplData });
            //this.el.find('.Theme').append(blogTypeView.el)
        },
        addAll: function(evt, data) {
            data = (data === undefined) ? this.collection._list : data;
            for( var i = 0, count = data.length; i < count; i++ ){
                this.addOne(evt, data[i]);
            }                       	
        },
        render: function(evt, data) {
            var self = this,
            	data = { Themes: self.collection.feed() };
            $.extend( data, self.tmplData );
            self.el.tmpl('livedesk>configure/themes', data, function(){
                //self.addAll(evt, data);
                self.el.find('[name="Theme"]').change();
            });        	
        },
    });
});