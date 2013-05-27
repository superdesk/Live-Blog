define([
    'jquery',
    'gizmo/superdesk',
    config.guiJs('superdesk/article', 'tabs/publishing-control'),
    config.guiJs('superdesk/article', 'models/target-type'),
    config.guiJs('superdesk/article', 'models/target-types'),
    'tmpl!superdesk/article>plugins/publishing-control'
], 
function($, giz, publishingControlTab, TargetType, TargetTypeCollection) {
    
	var PublishingControlTabBoxPlugin = giz.View.extend({
    	_parent: null,
    	_article: null,
    	_activatedOnce: false,
    	_targetTypeCollection: false,
    	events: {
    		'.sf-toggle-custom': {'click': 'toggleItem'}
    	},
    	init: function() {
    		var self = this;
    		this.el.appendTo($('section', publishingControlTab.content.el));
    		
    		$(publishingControlTab.content).on('active', function(){ self.activate(); });
            $(publishingControlTab.content).on('inactive', function(){ self.deactivate(); });
            
    		this._targetTypeCollection = new TargetTypeCollection;
    		this._targetTypeCollection.xfilter('*').sync().done(function(){
    			self.render();
    		});
    	},
    	render: function() {
    		$(this.el).tmpl('superdesk/article>plugins/publishing-control', {
    			targetTypes: this._targetTypeCollection.feed()
    		});
    	},
    	setParent: function(editView) {
            this._parent = editView;
        },
        setArticle: function(article) {
            var self = this;
            this._article = article;
            this._article.get('TargetType').xfilter('*').sync().done(function(){
				self._article.get('TargetType').each(function(){
	            	$('[data-target-type="' + decodeURIComponent(this.get('Key')) + '"]').prop('checked', true);
	            });
			});
        },
        
        deactivate: function()
        {
            $(this.el).addClass('hide');
        },
        
        activate: function() {
        	var self = this;
        	if (this._activatedOnce === false) {
        		// design specific code
        		$('.sf-toggle').each(function(i,val){
			      	var additional_class="";
			      	if ($(val).attr("checked")=="checked")  additional_class += " sf-checked ";
			      	if ($(val).hasClass("on-off")) additional_class +=" on-off-toggle ";
			      	if ($(val).hasClass("sf-disable")) additional_class += " sf-disable ";
			        $(val).wrap('<div class="sf-toggle-custom ' + additional_class + '"><div class="sf-toggle-custom-inner"></div></div>');
			        $(val).hide();
			    });
			    //
			    this._activatedOnce = true;
        	}
        	$(this.el).removeClass('hide');
        },
        toggleItem: function(e) {
        	e.preventDefault();
        	var item = e.currentTarget;
	        
	        // design specific code
	        if (!$(item).hasClass("sf-disable")) {
				$(item).toggleClass('sf-checked');
		        var own_box = $(item).find(".sf-toggle").first();
		        if (own_box.prop('checked')==true) {
		        	own_box.prop('checked',false);
		        } else {
		        	own_box.prop('checked',true);
		        }
	        }
	    	//
	    	this.updateArticle(own_box.data('target-type'), own_box.prop('checked'));
        },
        updateArticle: function(key, value) {
        	if (value === true) {
        		this._article.get('TargetType').update(key);
        	} else {
        		this._article.get('TargetType').delete(key);
        	}
        }
    });
    
    return new PublishingControlTabBoxPlugin;
});