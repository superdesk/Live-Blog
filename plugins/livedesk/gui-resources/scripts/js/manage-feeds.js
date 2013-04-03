define([
    'jquery',
    'gizmo/superdesk',
    'tmpl!livedesk>layouts/livedesk',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
	'tmpl!livedesk>manage-feeds',
], function ($, Gizmo) {

    /**
     * Manage Feeds Main View
     */
    var ManageFeedsView = Gizmo.View.extend({
        el: '#area-main',

        init: function() {
            this.model.one('read', this.render, this);
        },

        render: function() {
            var view = this;
            var data = this.model.feed();
	        $.tmpl('livedesk>manage-feeds', data, function(e,o){
		        $(view.el).html(o);

                $('.sf-checkbox').each(function(i,val){
                    $(val).after('<span class="sf-checkbox-custom" target-checkbox="' + $(val).attr('name') +'"></span>');
                    $(val).hide();
                });

                $('.sf-checkbox-custom').click(function(e){
                    e.preventDefault();
                    $(this).toggleClass('sf-checked');
                    var own_box = $('input[name="' + $(this).attr("target-checkbox") + '"]');
                    //set active class

                    var set_bg = own_box.attr("set-bg"); 
                    if (typeof set_bg !== undefined && set_bg !== false) {
                    $(this).parents().eq(set_bg-1).toggleClass('active-bg');
                    }
        
        
                    if (own_box.prop('checked')==true) { 
                    own_box.prop('checked',false); 
                    }
                    else { 
                    own_box.prop('checked',true); 
                    }
                    return false;
                    
                });

                $(".chain-source-collapse a").click(function(e){
       		            $(this).parents().eq(2).toggleClass("chain-collapsed");
                });
            });
            return this;
        }
    });

    return function(blogHref) {
        view = new ManageFeedsView({
            model: Gizmo.Auth(new Gizmo.Register.Blog(blogHref))
        });

        view.model.sync();
    }
});
