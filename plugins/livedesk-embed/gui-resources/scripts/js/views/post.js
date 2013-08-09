define([
	'jquery',
	'gizmo/superdesk',
	'jquery/tmpl',
	'jquery/utils',
	'utils/encode_url',
	'views/post-templates'
], function( $, Gizmo ) {
	return Gizmo.View.extend ({
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
				publishedOn, createdOn, baseTheme, item;
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
				data.CreatedOn = createdOn.format(_('postDate'));
				data.CreatedOnISO = createdOn.getTime();
			}
			if(data.PublishedOn) {
				publishedOn = new Date(Date.parse(data.PublishedOn));
				data.PublishedOn = publishedOn.format(_('postDate'));
				data.PublishedOnISO = publishedOn.getTime();
			}
			if(data.Content && liveblog.adminServer) {
				data.Content = data.Content.replace(liveblog.adminServer,livedesk.frontendServer);
			}
			
			if(data.Author.Source.IsModifiable ===  'True' || data.Author.Source.Name === 'internal') {
				item = "/item/posttype/"+data.Type.Key;
			}
			else if(data.Author.Source.Name === 'google')
				item = "/item/source/google/"+data.Meta.type;
			else
				item = "/item/source/"+data.Author.Source.Name;
			item = (require.defined('theme'+item))? 'theme'+item: 'themeBase'+item;
			data.baseItem = (require.defined('theme/item/base'))? 'theme/item/base': 'themeBase/item/base';

			$.tmpl(item, data, function(e, o){
				 self.setElement(o);
			});
					
		}
	});
});