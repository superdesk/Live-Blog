/*!
 * @author Mihai Balaceanu <mihai.balaceanu@sourcefabric.org>
 * @package 
 * @subpackage 
 * @copyright 2012 Sourcefabric o.p.s.
 * @license http://www.gnu.org/licenses/gpl.txt
 */

define(['jquery','jquery/superdesk','jquery/rest'], function ($,superdesk)
{
	return { init: function(){ superdesk.getActions('modules.country.*')
	.done(function(actions){
		$(actions).each(function()
		{  
			switch(this.Path)
			{
				case 'modules.country.list': listPath = this.ScriptPath; break;
				case 'modules.country.update': updatePath = this.ScriptPath; break;
				case 'modules.country.add': addPath = this.ScriptPath; break;
			}
		});
		require([superdesk.apiUrl+listPath], function(ListApp) {
			listApp = new ListApp({updateScript: updatePath, addScript: addPath});
		});		
	})}};
});