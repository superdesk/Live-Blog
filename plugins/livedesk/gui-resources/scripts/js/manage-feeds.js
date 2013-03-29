define([
	'jquery',
	'tmpl!livedesk>manage-feeds'
	], function ($) {
	
	$.tmpl('livedesk>manage-feeds',{}, function(e,o){
		$('#area-main').html(o);

      

      /* CUSTOM CHECKBOXES */
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




       /* COLLAPSE */

       $(".chain-source-collapse a").click(function(e){
       		$(this).parents().eq(2).toggleClass("chain-collapsed");
       });


	});
});