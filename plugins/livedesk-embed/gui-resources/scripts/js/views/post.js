define([
	'jquery',
	'gizmo/superdesk'
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
		itemTemplate: function(item, content, time, Avatar)
		{
			// Tw------------------------------------------------------------------------------------------------
			var returned = '';
							var itemClass = item.getClass();
							var author = item.get('AuthorName');
							var annotBefore = '';
							var annotAfter = '';
							if (item.data.hasOwnProperty('Meta')) {
								var Meta = item.data.Meta;
								if ( typeof Meta == 'string') {
									Meta = JSON.parse(Meta);
								}
								if ( Meta.hasOwnProperty('annotation') ) {
									if( typeof Meta.annotation === 'string' ) {
										if((Meta.annotation === '<br>') || (Meta.annotation === '<br/>') || (Meta.annotation === '<br />'))
											Meta.annotation = '';										
										annotAfter = '<div class="editable annotation">' + Meta.annotation + '</div>';   
									} else {
										if( Meta.annotation[1] !== null) {
											if((Meta.annotation[0] === '<br>') || (Meta.annotation[0] === '<br/>')|| (Meta.annotation[0] === '<br />') )
												Meta.annotation[0] = '';
											if((Meta.annotation[1] === '<br>') || (Meta.annotation[1] === '<br/>') || (Meta.annotation[1] === '<br />'))
												Meta.annotation[1] = '';											
											annotBefore = '<div class="editable annotation">' + Meta.annotation[0] + '</div>';
											annotAfter = '<div class="editable annotation">' + Meta.annotation[1] + '</div>';
										} else {
											if((Meta.annotation[0] === '<br>') || (Meta.annotation[0] === '<br/>')|| (Meta.annotation[0] === '<br />') )
												Meta.annotation[0] = '';											
											annotAfter = '<div class="editable annotation">' + Meta.annotation[0] + '</div>';
										}											
									}
								}
							}
							avatarString = '';
							if(_('no_avatar') != 'true' && Avatar.length > 0 && author != 'twitter') {
								avatarString = '<figure><img src="' + Avatar + '" ></figure>';
							}                                
							switch (itemClass) {
								case 'tw':
								case 'service':
									returned += annotBefore;
									returned += avatarString;
									returned +=  '<div class="result-content">';
									if ( author == 'twitter') {
										returned += '<blockquote class="twitter-tweet"><p>' + content + '</p>&mdash; ' + Meta.from_user_name + ' (@' + Meta.from_user_name + ') <a href="https://twitter.com/' + Meta.from_user + '/status/' + Meta.id_str + '" data-datetime="'+Meta.created_at+'"></a></blockquote>';
										
										if ( !window.livedesk.loadedTweeterScript || 1) {
											window.livedesk.loadScript('//platform.twitter.com/widgets.js', function(){});
											window.livedesk.loadedTweeterScript = true;
										}
									} else if ( author == 'youtube') {
										
										returned +=     '<div class="result-text">' + content + '</div>';
										returned +=     '<p class="attributes"><i class="source-icon"></i> '+_('by')+' ';										
										returned +=     '<a class="author-name" href="http://youtube.com/'+Meta.uploader+'" target="_blank">'+Meta.uploader+'</a>';
									} else if ( author == 'google'){
										//titleNoFormatting
										returned +=     '<h3><a target="_blank" href="'+Meta.unescapedUrl+'">'+Meta.title+'</a></h3>'
										returned +=     '<div class="result-text">' + content + '</div>';
										//returned +=     '<p class="attributes"><i class="source-icon"><img src="http://g.etfv.co/'+Meta.url+'" style="max-width: 16px" border="0"></i><a class="author-name" href="'+Meta.url+'">'+Meta.visibleUrl+'</a>'
										returned +=     '<p class="attributes"><i class="source-icon"></i> '+_('by')+' ' + item.get('AuthorName');
									} else if (author == 'flickr') {
										returned +=     '<div class="result-text">' + content + '</div>';
										returned +=     '<p class="attributes"><i class="source-icon"></i> '+_('by')+' ' + item.get('AuthorName');										
									}
									else {
										returned +=     '<div class="result-text">' + content + '</div>';
										returned +=     '<p class="attributes"><i class="source-icon"></i> '+_('by')+' ' + item.get('AuthorName');
										returned +=         '<time>' + time + '</time>';
									}
									returned +=     '</p>';
									returned += '</div>';
									returned += annotAfter;
									
									break;
								case 'quotation':
									var adition, authorName = item.get('AuthorName'), auxDiv = content.split('<div><br><br></div>'), auxBr = content.split('<br><br><br>');
									if(auxDiv.length == 2) {
										content = auxDiv[0];
										adition = '<div class="quotation-author">'+auxDiv[1]+'</div>';
									} else if (auxBr.length == 2) {
										content = auxBr[0];
										adition = '<div class="quotation-author">'+auxBr[1]+'</div>';
									}
									//returned += avatarString;
									returned +=  '<div class="result-content">';
									returned +=     '<div class="result-text">' + content + '</div>';
									if(adition)
										returned += adition;
									else
										returned +=     '<div class="attributes">'+_('by')+' ' + authorName + '</div>';
									returned += '</div>';
									break;
								case 'wrapup':
									returned += '<span class="big-toggle"></span>';
									returned += '<h3>' + content + '</h3>';
									break;
								case 'advertisement':
									returned += content;
									
							}
						   return returned;
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
								item.nextUntil('.wrapup').hide();
							} else {
								//don't collapse wrap'
							}
						} else {
							item.removeClass('closed').addClass('open');
							item.nextUntil('.wrapup').show();
						}
					},
					togglePermalink: function(e) {
						this._togglePermalink($(e).next('input[data-type="permalink"]'));
					},
					_togglePermalink: function(item) {
						if (item.css('visibility') == 'visible') {
						   item.css('visibility','hidden');
						} else {
						   item.css('visibility', 'visible');
						}
					},
		render: function()
		{
		
			var self = this, order = parseFloat(self.model.get('Order')), Avatar='';
			if(this.model.get('AuthorPerson') && this.model.get('AuthorPerson').EMail) {
				Avatar = $.avatar.get(self.model.get('AuthorPerson').EMail);
			}
			if ( !isNaN(self.order) && (order != self.order)) {
				self.order = order;
				self._parent.reorderOne(self);
			}
			var content = self.model.get('Content');

			var style= '';                
			if (self.model.getClass() == 'wrapup') {
				style += 'open ';
			}
			if (self.model.isService()) {
				style += self.model.get('AuthorName');
									
				var meta = JSON.parse(self.model.get('Meta'));
				
				var publishedon = self.model.get('PublishedOn');
				var datan = new Date(publishedon);
				var time = datan.format('ddd mmm dd yyyy HH:MM:ss TT');
									
				if (self.model.get('AuthorName') == 'flickr') {
					var paddedContent = '<span>' + content + '</span>';
					var jqo = $(paddedContent);
					jqo.find('img').attr('src', jqo.find('a').attr('href'));
					content = jqo.html();
				} else if (self.model.get('AuthorName') == 'twitter') {
											Avatar = meta.profile_image_url;
					content = self.model.twitter.link.all(content);
				} else if (self.model.get('AuthorName') == 'google') {
										if (meta.tbUrl) {
											content += '<p><a href="' + meta.url + '"><img src="' + meta.tbUrl + '" height="' + meta.tbHeight + '" width="' + meta.tbWidth + '"></a></p>';
										}
									}
			}
																						 
			var publishedon = self.model.get('PublishedOn');
			var datan = new Date(publishedon);
			var time = datan.format(_('ddd mmm dd yyyy HH:MM:ss TT'));
			if(_('show_current_date') === 'true')
			{
				var currentDate = new Date();
				if(currentDate.format('mm dd yyyy') == datan.format('mm dd yyyy'))
					time = datan.format(_('HH:MM:ss TT'));
			}
			var author = self.model.get('AuthorName');
			
			content = self.itemTemplate(self.model, content, time, Avatar);
							
			/*var postId = self.model.get('Id');
			var blogTitle = self._parent.model.get('Title');
			blogTitle = blogTitle.replace(/ /g, '-');
			var hash = postId + '-' +  encodeURI (blogTitle);
			*/
			var hash = self.model.get('Order');
			var itemClass = self.model.getClass();
			var fullLink = window.livedesk.location + '#' + self._parent.hashIdentifier + hash;
			var permalink = '';
			if(itemClass !== 'advertisement' && itemClass !== 'wrapup')
				permalink = '<a rel="bookmark" href="#'+ self._parent.hashIdentifier + hash +'">#</a><input type="text" value="' + fullLink + '" style="visibility:hidden" data-type="permalink" />';						
			var template ='<li class="'+ style + itemClass +'"><a name="' + hash + '"></a>' + content + '&nbsp;'+ permalink +'</li>';
							
			if ( typeof window.livedesk.productionServer != 'undefined' && typeof window.livedesk.frontendServer != 'undefined' ){
				re = new RegExp(window.livedesk.productionServer, "g");
				template = template.replace(re, window.livedesk.frontendServer );
			}

			self.setElement( template );
			self.model.triggerHandler('rendered');
			$(self.el).off('click.livedesk', '.big-toggle').on('click.livedesk', '.big-toggle', function(){
				self.toggleWrap(this, true);
			});
			$(self.el).off('click.livedesk', 'a[rel="bookmark"]').on('click.livedesk', 'a[rel="bookmark"]', function() {
				self.togglePermalink(this);
			});
			$(self.el).off('click.livedesk', 'input[data-type="permalink"]').on('focus.livedesk click.livedesk', 'input[data-type="permalink"]', function() {
				$(this).select();
			});
		}
	});
});