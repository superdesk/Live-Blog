define(['jquery', 'jqueryui/mouse', 'tmpl!sandbox>sandbox','tmpl!sandbox>item', 'tmpl!sandbox>new'], function($)
{
    $.superdesk.hideLoader();
    $('#area-main').tmpl('sandbox>sandbox',{persons: [{name:'Billy'},{name: 'Mihai'}]});
    // more code here


	$('#sandbox-button').on('click', function(){ $('#sandbox-place').tmpl('sandbox>new'); });
    
});