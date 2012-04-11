/*!
 * @author Mihai Balaceanu <mihai.balaceanu@sourcefabric.org>
 * @package 
 * @subpackage 
 * @copyright 2012 Sourcefabric o.p.s.
 * @license http://www.gnu.org/licenses/gpl.txt
 */
define([
  'jquery','jquery.superdesk','jquery.tmpl','jquery.rest',
  'tmpl!layouts/list',
  'tmpl!country>list',
  'tmpl!country>list-head',
  'tmpl!country>list-body',
  'tmpl!country>list-footer',
  ], function($, superdesk){ 
var ListApp = function( paths ) {
	var countries,
		presentation = this,
		app = function()
		{
			$('#area-main').tmpl('layouts/list');
			
			$('#area-content').html( $('<table class="table table-bordered table-striped country-list" />').datatable
			({
				tpl: 
				{
					header: 'list-head',
					footer: 'list-footer',
					body: 'list-body',
				},
				resource: new $.rest(superdesk.apiUrl + '/resources/Superdesk/Country').xfilter('Code, Name')
			}));
			
			//$('#area-content').append( $($.tmpl($("#tpl-country-add", superdesk.tmplRepo))) );
		};
		
		//presentation.view.load('country/templates/list.html').done(app);

	// details button functionality 
	$(document)
	.off('click.superdesk-country-list', '.country-list .btn-info')
	.on('click.superdesk-country-list', '.country-list .btn-info', function(event)
	{
		new $.rest($(this).attr('href')).done(function(data)
		{
			$( $.tmpl($('#tpl-country-details', superdesk.tmplRepo), data) )
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
}
return ListApp;
});

