var jqueryScriptNode = document.createElement('script');
var superdesk =  
{ 
	libUri: "{libUri}",
	_requireQueue: [],
	require: function(scriptPath)
	{
		this._requireQueue.push(scriptPath);
	},
	_postRequire: function(script)
	{
		$('<script />').attr('src', superdesk.libUri+script).appendTo(document.head);
	}
};
jqueryScriptNode.addEventListener('load', function()
{ 
	superdesk.require = superdesk._postRequire;
	delete superdesk._postRequire;
	for(var i in superdesk._requireQueue)
		superdesk.require(superdesk._requireQueue[i])
	delete superdesk._requireQueue;
});
addJQuery = function()
{
	jqueryScriptNode.setAttribute('src', superdesk.libUri+'jquery.js');
	var headChildren = document.head.children;
	for(var i in headChildren)
		if(headChildren[i].tagName.toLowerCase() == 'script')
		{
			document.head.insertBefore(jqueryScriptNode, headChildren[i]);
			break;
		}
};
if( document.addEventListener ) 
	window.addEventListener( "load", addJQuery, false );
else if( document.attachEvent ) 
	window.attachEvent( "onload", addJQuery );
