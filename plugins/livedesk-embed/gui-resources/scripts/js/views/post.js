define([
	'jquery',
	'gizmo/superdesk',
	'jquery/tmpl',
	'jquery/utils',
	'tmpl!theme/item/base',
	'tmpl!theme/item/item',
	'tmpl!theme/item/annotated',
	'tmpl!theme/item/social-share',
	'tmpl!theme/item/posttype/normal',
	'tmpl!theme/item/posttype/wrapup',
	'tmpl!theme/item/posttype/quote',
	'tmpl!theme/item/posttype/link',
	'tmpl!theme/item/source/advertisement',	
	'tmpl!theme/item/source/google',
	'tmpl!theme/item/source/twitter',
	'tmpl!theme/item/source/youtube',
	'tmpl!theme/item/source/flickr',
	'tmpl!theme/item/source/soundcloud',
	'tmpl!theme/item/source/instagram'
], function( $, Gizmo ) {
	return Gizmo.View.extend ({
		init: function()
		{
					var self = this;
					self.xfilter = 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
							   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta';
					self.model
							.on('read update', function(evt, data){
									/**
									 * Quickfix.
									 * @TODO: make the isCollectionDelete check in gizmo before triggering the update.
									 */
					   				if( self._parent.model.get('PostPublished').isCollectionDeleted(self.model) )
										return;
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
		remove: function(evt)
		{
			var self = this;
			self._parent.removeOne(self);
			self.el.remove();
			self.model.off('read update delete');
			return self;			
		},
		toggleWrap: function(e, forceToggle) {
			if (typeof forceToggle != 'boolean' ) {
				forceToggle = false;
			}
			this._toggleWrap($(e).closest('li').first(), forceToggle);
		},
		_toggleWrap: function(item, forceToggle) {
			if (typeof forceToggle != 'boolean' ) {
				forceToggle = false;
			}
			if (item.hasClass('open')) {
				var collapse = true;
				if ( collapse ) {
					item.removeClass('open').addClass('closed');
					item.nextUntil('.wrapup,#loading-more').hide();
				} else {
					//don't collapse wrap'
				}
			} else {
				item.removeClass('closed').addClass('open');
				item.nextUntil('.wrapup,#loading-more').show();
			}
		},		
		render: function(evt, data)
		{
			var self = this, 
				data = self.model.feed(),
				order = parseFloat(self.model.get('Order'));
			if ( !isNaN(self.order) && (order != self.order)) {
				self.order = order;
				self._parent.reorderOne(self);
			}
			data.HashIdentifier = self._parent.hashIdentifier;
			if(data.Meta) {

				data.Meta = JSON.parse(data.Meta);
				if(data.Meta.annotation[1] === null) {
					data.Meta.annotation = data.Meta.annotation[0];
					data.Meta.annotation = $.trimTag(['<br>', '<br />'], data.Meta.annotation);
				}

				if ( typeof data.Meta.annotation !== 'string') {
					var aux = data.Meta.annotation;
					data.Meta.annotation = {
						'before': $.trimTag(['<br>', '<br />'], aux[0]), 
						'after': $.trimTag(['<br>', '<br />'], aux[1])
					}
				} else {
					data.Meta.annotation = $.trimTag(['<br>', '<br />'], data.Meta.annotation);
				}
			}
			data.permalink = self._parent.location + '#' + self._parent.hashIdentifier + data.Order;			
			if(data.Author.Source.Name !== 'internal') {
				data.item = "source/"+data.Author.Source.Name;
			}
			else if(data.Type)
				data.item = "posttype/"+data.Type.Key;
			//console.log(data.Author.Source.Name,data.item);
			$.tmpl('theme/item/item',data, function(e, o){
				if(!e) {
					self.setElement(o);
					var input = $('input[data-type="permalink"]',self.el);
					$('a[rel="bookmark"]', self.el).on(self.getEvent('click'), function(evt) {
						//evt.preventDefault();
						if(input.css('visibility') === 'visible') {
							input.css('visibility', 'hidden' );
						} else {
							input.css('visibility', 'visible' );
							input.trigger(self.getEvent('focus'));
							$('.result-header .share-box', self.el).fadeOut('fast');
						}
						
					});
					input.on(self.getEvent('focus')+' '+self.getEvent('click'), function() {
						$(this).select();
					});
					$('.big-toggle', self.el).off( self.getEvent('click') ).on(self.getEvent('click'), function(){
						self.toggleWrap(this, true);
					});

					var li = $('.result-header', self.el).parent();
					li.hover(function(){
						//hover in
					}, function(){
						$(this).find('.share-box').fadeOut(100);
						$('input[data-type="permalink"]', self.el).css('visibility', 'hidden');
					});

					var sharelink = $('.sf-share', self.el);
					sharelink.on(self.getEvent('click'), function(evt){
					    evt.preventDefault();
						var share = $(this);
						var added = share.attr('data-added');
						if ( added != 'yes') {
							var myPerm = escape(data.permalink);
							var imgsrc = $('.result-content img:first', self.el).attr('src');
							var pinurl = "http://pinterest.com/pin/create/button/?url=" + myPerm + "&media=" + imgsrc + "&description=";
							var gglurl = "https://plus.google.com/share?url=" + myPerm + "&t=";
							var emailurl = "mailto:?to=&subject=&body=" + myPerm;
							var socialParams = {
								'fbclick': "$.socialShareWindow('http://facebook.com/share.php?u=" + myPerm + "',400,570); return false;",
								'twtclick': "$.socialShareWindow('http://twitter.com/home?status=Reading:" + myPerm + "',400,570); return false;",
								'linclick': "$.socialShareWindow('http://www.linkedin.com/shareArticle?mini=true&url=" + myPerm + "', 400, 570); return false;",
								'pinclick': "$.socialShareWindow('" + pinurl + "', 400, 700); return false;",
								'gglclick': "$.socialShareWindow('" + gglurl + "', 400, 570); return false;",
								'emailclick': "$.socialShareWindow('" + emailurl + "', 1024, 768); return false;",
								'emailurl': emailurl
							}
							$.tmpl('theme/item/social-share', socialParams, function(e, o){
								share.after(o);
								share.attr('data-added', 'yes');	
							});
						}
						$('input[data-type="permalink"]', self.el).css('visibility', 'hidden');
						$(this).next('.share-box').toggle();
					})
				} else {
					console.error(e);
				}
			});
			setTimeout(function(){
				/*
				$.tmpl('theme/item/social-share', {'permalink': data.permalink}, function(e, o){
					$('.sf-share[data-shared!="yes"]').on('click', function(){
						var share = $(this);
						var added = share.attr('data-added');
						if ( added != 'yes') {
							var url = share.attr('data-added');
							share.after(o);
							share.attr('data-added', 'yes');
						}
						$(this).next('.share-box').toggle();
					});
				});	
				*/
			});
					
		}
	});
});