define([
	'jquery',
	'gizmo/superdesk',
	'jquery/tmpl',	
	'tmpl!theme/item/base',
	'tmpl!theme/item/item',
	'tmpl!theme/item/annotated',
	'tmpl!theme/item/posttype/normal',
	'tmpl!theme/item/posttype/wrapup',
	'tmpl!theme/item/posttype/quote',
	'tmpl!theme/item/posttype/advertisement',	
	'tmpl!theme/item/source/google',
	'tmpl!theme/item/source/twitter',
	'tmpl!theme/item/source/youtube',
	'tmpl!theme/item/source/flicker',
	'tmpl!theme/item/source/soundcloud',
	'tmpl!theme/item/source/instagram',	
], function( $, Gizmo ) {
	return Gizmo.View.extend ({
		init: function()
		{
					var self = this;
					self.xfilter = 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
							   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta';
					self.model
							.on('read update', function(evt, data){
									//console.log('this.data: ',$.extend({},this.data), ' is only:' ,isOnly(this.data, ['CId','Order']));
									/*if(isOnly(this.data, ['CId','Order']) || isOnly(data, ['CId','Order'])) {
											console.log('this.data: ',$.extend({},this.data));
											console.log('data: ',$.extend({}, data));
											console.log('force');
											self.model.xfilter(self.xfilter).sync({force: true});
									}
									else*/
									{
										self.render(evt, data);
									}
							})
							.on('delete', self.remove, self)
							.xfilter(self.xfilter)
							.sync();
		},
		remove: function()
		{
			var self = this;
			self._parent.removeOne(self);
			self.el.remove();
			return self;			
		},
		render: function()
		{
			var self = this, data = self.model.feed();
			data.HashIdentifier = self._parent.hashIdentifier;
			if(data.Meta) {
				data.Meta = JSON.parse(data.Meta);
				if(data.Meta.annotation[1] === null) {
					data.Meta.annotation = data.Meta.annotation[0];
					data.Meta.annotation = (data.Meta.annotation === '<br/>') || (data.Meta.annotation === '<br>') ? '' :  data.Meta.annotation;
				}
			}
			data.permalink = self._parent.location + '#' + self._parent.hashIdentifier + data.Order;			
			if(data.Author.Source.Name !== 'internal') {
				data.Item = "source/"+data.Author.Source.Name;
			}
			else if(data.Type)
				data.Item = "posttype/"+data.Type.Key;
			$.tmpl('theme/item/item',data, function(e, o){
				if(!e) {
					self.setElement(o);
					var input = $('input[data-type="permalink"]',self.el);
					$('a[rel="bookmark"]',self.el).on(self.getEvent('click'), function(evt) {
						evt.preventDefault();
						if(input.css('visibility') === 'visible') {
							input.css('visibility', 'hidden' );
						} else {
							input.css('visibility', 'visible' );
							input.trigger(self.getEvent('focus'));
						}
						
					});
					input.on(self.getEvent('focus')+' '+self.getEvent('click'), function() {
						$(this).select();
					});
					
				}
			});
		}
	});
});