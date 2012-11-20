define(['gizmo/superdesk', config.guiJs('livedesk', 'models/post')], 
function(giz, Post)
{
    return giz.Collection.extend(
	{ 
		model: Post,
		insertSync: function()
		{
            this.desynced = false;
            if( !(model instanceof Model) ) model = this.modelDataBuild(new this.model(model));
            this._list.push(model);
            model.hash();
            model.sync(this.href);
            return model;
		}		
	});
});