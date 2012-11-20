/*!
 * @author Mihai Balaceanu <mihai.balaceanu@sourcefabric.org>
 * @package 
 * @subpackage 
 * @copyright 2012 Sourcefabric o.p.s.
 * @license http://www.gnu.org/licenses/gpl.txt
 */
define
([
  'jquery','jquery/superdesk','jquery/tmpl','jquery/rest', 'jqueryui/datatable', 
  'tmpl!layouts/list',
  'tmpl!country>add',
  'tmpl!country>list',
  'tmpl!country>list-head',
  'tmpl!country>list-body',
  'tmpl!country>list-footer',
], 
function($, superdesk)
{
    var datatable = $('<table class="table table-bordered table-striped country-list" />').datatable
    ({
        tpl: 
        {
            header: 'country>list-head',
            footer: 'country>list-footer',
            body: 'country>list-body'
        },
        resource: new $.rest('Superdesk/Country').xfilter('Code, Name')
    });
    
    var ListApp = function( paths ) 
    {
        $('#area-main').tmpl('country>list', {ui:{ content: 'is-content=1'}});
        $('#area-main [is-content]').html( datatable );
        
    	$.tmpl('country>add', {}, function(error, output){ $('#area-content').append(output); });
    
    	// details button functionality 
    	$(document)
    	.off('click.superdesk-country-list', '.country-list .btn-info')
    	.on('click.superdesk-country-list', '.country-list .btn-info', function(event)
    	{
    		new $.rest($(this).attr('href')).done(function(data)
    		{
    			require(['jquery','jqueryui/dialog','tmpl!country>details',], function($) {
    				$.tmpl('country>details', data, function(error, output) {
    					$(output)
    					.dialog
    					({ 
    						draggable: false,
    						resizable: false,
    						modal: true,
    						width: "40.1709%",
    						close: function(){ $(this).dialog('destroy').remove(); },
    						buttons: 
    						[{
    							text: "Close",
    							click: function(){ $(this).dialog('close'); },
    							class: "btn btn-primary"
    						}]
    					});
    
    				});
    			});
    		});
    		event.preventDefault();
    	});
    	$(document)
    	.off('click.superdesk-country-list', '.country-add.btn')
    	.on('click.superdesk-country-list', '.country-add.btn', function(event)
    	{
    		superdesk.navigation.bind('/country/add', function()
    		{
    			console.log('add country');
    		});
    		event.preventDefault();
    	});	
    };
    
return ListApp;

});

