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

	/*
	//sample 1:
	superdesk.navigation.bind('/country/list', function()
	{
	    (new superdesk.presentation)
	        .setScript(listPath)
		    .setLayout(superdesk.layouts.list.clone())
		    .setArgs({updateScript: updatePath, addScript: addPath})
		    .run();
	}, 'Country list');
	
	//sample 2:
	(new superdesk.presentation).direct
	({ 
	    href: '/country/list', 
	    script: listPath, 
	    layout: superdesk.layouts.list.clone(), 
	    args: {updateScript: updatePath, addScript: addPath}, 
	    title 'Country list'
	});
	
	sample 3:
	*/
	(new superdesk.presentation).direct( '/country/list', listPath, superdesk.layouts.list.clone(), {updateScript: updatePath, addScript: addPath}, 'Country list' );  
});
