define([
	'gizmo/superdesk'
], function(giz){
	var TargetType = giz.Model.extend({
    	url: new giz.Url('Content/TargetType')
    });
    
    return TargetType;
});