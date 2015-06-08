 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'models/themes'),
    'tmpl!livedesk>configure/themes',
    'tmpl!livedesk>configure/embed',
    'tmpl!livedesk>configure/embed-simple',
    'tmpl!livedesk>configure/embed-http'    
], function( $, Gizmo) {
   return Gizmo.View.extend({
        tmplData: {},
        tmplId: 'livedesk>configure/embed-http',
        events: {
        	'[name="Theme"]': { change: 'change'}
        },
        init: function() {
            var self = this;
            if( !self.collection ) {
                self.collection = Gizmo.Auth ( new Gizmo.Register.Themes() );
            }
            self.dfdCollection = self.collection
                .on('read update', self.render, self)
                .xfilter('Name,URL')
                .sync();          
        },
        changeTmpl: function(value) {
            if(value) {
                this.tmplId = 'livedesk>configure/embed-simple';
            } else {
                this.tmplId = 'livedesk>configure/embed';
            }
            this.change();
        },
        change: function(evt) {
        	var self = this;
            self.dfdCollection.done(function(){
                var el = self.el.find('[name="Theme"]'),
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
            	for( var i = 0, count = self.collection._list.length; i < count; i++ ){
            		theme = self.collection._list[i];
            		if(theme.get('Name') === el.val()) {
            			break;
            		}
            	}
                blogUrl = self.theBlog;
                /*!
                 * If the blog url doesn't have servername in it add it
                 *   else replace with the frontend server.
                 */
                var frontendServer = $('[name="FrontendServer"]').val();
                if(blogUrl.indexOf(config.api_url) !== -1) {
                    blogUrl = blogUrl.replace(config.api_url, frontendServer);
                } else {
                    blogUrl = frontendServer + blogUrl;
                }

                var frontendServerArray = frontendServer.toLowerCase().split("//"),
                    protocol = frontendServerArray[0],
                    themeNoProtocol;
                    frontendServerArray.shift();
                    frontendServer = "//" + frontendServerArray.join("//");
                // @TODO: force http protocol.
                protocol = 'http:';
                themeNoProtocol = theme.get('URL').href.replace('\\','/').split("//")
                themeNoProtocol.shift();
                themeNoProtocol = "//" + themeNoProtocol.join('//');
                themePath = themeNoProtocol.replace(config.api_url, frontendServer);
                data = {
                    'Theme': el.val(),
                    'Id': self._parent.model.get('Id'),
                    'GuiLivedeskEmbed': protocol + frontendServer + '/content/' + config.guiJs('livedesk-embed','core/require.js'),
                    'ApiUrl': config.api_url,
                    'FrontendServer': protocol + frontendServer,
                    'Language': optionLanguage.attr('data-code')
                }
            	$.tmpl(self.tmplId, data, function(e,o){
            		$('#emebed-script')
            		.val(o)
            		.focus();
            	});
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