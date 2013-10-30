				// pass functionallity to provider if exists
				if( providers[src] && providers[src].timeline )
				{
				    providers[src].timeline.preData && providers[src].timeline.preData.call(self);
				    if( providers[src].timeline.render ) 
				    {
				        providers[src].timeline.render.call(self, function()
				        {
				        	var that = this;
				        	BlogAction.get('modules.livedesk.blog-publish').done(function(action) {
				            	$('.editable', that.el).texteditor({plugins: {controls: timelinectrl}, floatingToolbar: 'top'});
				            }).fail(function(action){
				            	self.el.find('.unpublish,.close').remove();
				            	if(self.model.get('Creator').Id == localStorage.getItem('superdesk.login.id'))
				            		self.el.find('.editable').texteditor({plugins: {controls: timelinectrl}, floatingToolbar: 'top'});
				            });
				            $(self).triggerHandler('render');
				        });
				        rendered = true;
				    }
				}
				
				!rendered &&
				$.tmpl('livedesk>timeline-item', {Post: post}, function(e, o)
				{
					self.setElement(o);
					BlogAction.get('modules.livedesk.blog-publish').done(function(action) {
						self.el.find('.editable').texteditor({plugins: {controls: timelinectrl}, floatingToolbar: 'top'});
		            }).fail(function(action){
		            	self.el.find('.unpublish,.close').remove();
		            	if(self.model.get('Creator').Id == localStorage.getItem('superdesk.login.id'))
							self.el.find('.editable').texteditor({plugins: {controls: timelinectrl}, floatingToolbar: 'top'});
					});
					/*!
                     * conditionally handing over some functionallity to provider if
                     * model has source name in providers 
                     */
                    if( providers[src] && providers[src].timeline ) {
						providers[src].timeline.init.call(self);
					}
                    
                    $(self).triggerHandler('render');
					
				});