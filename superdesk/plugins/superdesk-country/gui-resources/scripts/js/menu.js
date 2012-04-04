/*!
 * @author Mihai Balaceanu <mihai.balaceanu@sourcefabric.org>
 * @package 
 * @subpackage 
 * @copyright 2012 Sourcefabric o.p.s.
 * @license http://www.gnu.org/licenses/gpl.txt
 */
var listPath, updatePath, addPath;
superdesk.getActions('modules.country.*')
.done(function(actions)
{
	$(actions).each(function()
	{  
		switch(this.Path)
		{
			case 'modules.country.list': listPath = this.ScriptPath; break;
			case 'modules.country.update': updatePath = this.ScriptPath; break;
			case 'modules.country.add': addPath = this.ScriptPath; break;
		}
	});

	(new superdesk.presentation)
		.setScript(listPath)
		.setLayout(superdesk.layouts.list.clone())
		.setArgs({updateScript: updatePath, addScript: addPath})
		.run();
});
