define([
	'jquery',
	'gizmo/superdesk',
	'dust',
	'jquery/tmpl',
	'jquery/utils',
	'utils/encode_url',
	'utils/date-format',
	'views/post-templates'
], function( $, Gizmo, dust ) {
	return function(){
		var PostView = Gizmo.View.extend ({
			data: {},
			init: function()
			{
				var self = this;
				self.model
						.on('read update', function(evt, data){
								/**
								 * Quickfix.
								 * @TODO: make the isCollectionDelete check in gizmo before triggering the update.
								 */
				   				if( self._parent.collection.isCollectionDeleted(self.model) )
									return;
								self.render(evt, data);
						})
						.on('delete', self.remove, self)
						//.xfilter(self.xfilter)
						//.sync();
				self.render();
			},
			remove: function(evt)
			{
				var self = this;
				self._parent.removeOne(self);
				self.el.remove();
				self.model.off('read update delete');
				return self;			
			},	
			render: function(evt, data)
			{
				var self = this, 
					data = self.model.feed(true),
					order = parseFloat(self.model.get('Order')),
					publishedOn, createdOn, baseTheme, shortItem;
				self.templateData = data;
				if ( !isNaN(self.order) && (order != self.order)) {
					self._parent.orderOne(self);
				}
				if(data.Meta) {
					data.Meta = $.parseJSON(data.Meta);
				}
				if(data.Meta && data.Meta.annotation) {
					if(data.Meta.annotation[1] === null) {
						data.Meta.annotation = data.Meta.annotation[0];
						data.Meta.annotation = $.trimTag(['<br>', '<br />'], data.Meta.annotation);
					}
					if ( typeof data.Meta.annotation !== 'string') {
						if(data.Meta.annotation[0]) {
							var aux = data.Meta.annotation;
							data.Meta.annotation = {
								'before': $.trimTag(['<br>', '<br />'], aux[0]), 
								'after': $.trimTag(['<br>', '<br />'], aux[1])
							}
						} else {
							data.Meta.annotation = {
								'before': $.trimTag(['<br>', '<br />'], data.Meta.annotation.before), 
								'after': $.trimTag(['<br>', '<br />'], data.Meta.annotation.after)
							}					
						}
					} else {
						data.Meta.annotation = $.trimTag(['<br>', '<br />'], data.Meta.annotation);
					}
				}

				if(data.CreatedOn) {
					createdOn = new Date(Date.parse(data.CreatedOn));
					data.CreatedOn = createdOn.format(_('post-date'));
					data.CreatedOnISO = createdOn.getTime();
				}
				if(data.PublishedOn) {
					publishedOn = new Date(Date.parse(data.PublishedOn));
					data.PublishedOn = publishedOn.format(_('post-date'));
					data.PublishedOnISO = publishedOn.getTime();
				}
				if(data.Content && liveblog.adminServer) {
					data.Content = data.Content.replace(liveblog.adminServer,livedesk.frontendServer);
				}
				
				if(data.Author.Source.IsModifiable ===  'True' || data.Author.Source.Name === 'internal') {
					if(data.Type.Key === 'advertisement') {
						self.item = "/item/posttype/infomercial";
					}
					else {
						self.item = "/item/posttype/"+data.Type.Key;
					}
				}
				else if(data.Author.Source.Name === 'google')
					self.item = "/item/source/google/"+data.Meta.type;
				else {
					if(data.Author.Source.Name === 'advertisement') {
						self.item = "/item/source/infomercial";
					} else {
						self.item = "/item/source/"+data.Author.Source.Name;
					}
				}
				shortItem = self.item;
				self.item = (dust.defined('theme'+self.item))? 'theme'+self.item: 'themeBase'+self.item;
				data.baseItem = (dust.defined('theme/item/base'))? 'theme/item/base': 'themeBase/item/base';
				data.frontendServer = liveblog.frontendServer;
				$.dispatcher.triggerHandler('post-view.render-' + shortItem, self);
				$.each(self.data, function(key, value){
					if($.isFunction(value)){
						data[key] = value.call(self, data);	
					} else {
						data[key] = value;
					}
				});
				$.tmpl(self.item, data, function(e, o){
					self.setElement(o);
					/*!
					 * @TODO Move this into a plugin
					 */
					var sharelink = $('.sf-share', self.el);
					sharelink.on(self.getEvent('click'), function(evt){
					    evt.preventDefault();
						var share = $(this);
						var added = share.attr('data-added');
						if ( added != 'yes') {
							var blogTitle = encodeURL(self._parent._parent.model.get('Title'));
							var myPerm = encodeURL(data.permalink);
							var imgsrc = $('.result-content img:first', self.el).attr('src');
							if ( !imgsrc ) {
								var imgsrc = $('img:first').attr('src');
							}
							var summary = encodeURL($('.result-content .result-text:last', self.el).text());
							var pinurl = "http://pinterest.com/pin/create/button/?url=" + myPerm + "&media=" + imgsrc + "&description=" + blogTitle;
							var gglurl = "https://plus.google.com/share?url=" + myPerm + "&t=";
							var emailurl = "mailto:?to=&subject=" + _('Check out this Live Blog') + "&body=" + myPerm;
							var fburl = "http://www.facebook.com/sharer.php?s=100";
							fburl += '&p[title]=' + blogTitle;
							fburl += '&p[summary]=' + summary;
							fburl += '&p[url]=' + myPerm;
							var i = 0;
							$('.result-content img', self.el).each(function(){
								var src = $(this).attr('src');
								fburl += '&p[images][' + i + ']=' + src;
								i ++;
							});
							

							var socialParams = {
								'fbclick': "$.socialShareWindow('" + fburl + "',400,570); return false;",
								'twtclick': "$.socialShareWindow('http://twitter.com/home?status=" + _('Now reading ') + blogTitle + ": " + myPerm + "',400,570); return false;",
								'linclick': "$.socialShareWindow('http://www.linkedin.com/shareArticle?mini=true&url=" + myPerm + "&title=" +  blogTitle + "&summary=" + summary + "', 400, 570); return false;",
								'pinclick': "$.socialShareWindow('" + pinurl + "', 400, 700); return false;",
								'gglclick': "$.socialShareWindow('" + gglurl + "', 400, 570); return false;",
								'emailclick': "$.socialShareWindow('" + emailurl + "', 1024, 768); return false;",
								'emailurl': emailurl
							}
							$.tmpl('themeBase/item/social-share', socialParams, function(e, o){
								share.after(o);
								share.attr('data-added', 'yes');	
							});
						}
						var propName = 'visibility',
							propValue = { 'show': 'visible', 'hide': 'hidden' },
							box = $('[data-gimme="post.share-social"]',self.el);
						if(box.css(propName) === propValue.show) {
							box.css(propName, propValue.hide );
						} else {
							$('[data-gimme^="post.share"]',self.el).css(propName, propValue.hide);
							box.css(propName, propValue.show );
						}
					});
					/*!
					 * @END TODO
					 */
					 $.dispatcher.triggerHandler('post-view.rendered-after-' + shortItem, self);
				});
						
			}
		});
		$.dispatcher.triggerHandler('post-view.class',PostView);
		return PostView;
	}
});