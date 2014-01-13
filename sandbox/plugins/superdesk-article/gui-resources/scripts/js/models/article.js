define([ 'gizmo/superdesk', config.guiJs('superdesk/article', 'models/article-ctx') ],
function(giz, ArticleCtx)
{
    // article demo model
    return giz.Model.extend
    ({ 
        defaults: { ArticleCtx: giz.Collection.extend({ model: ArticleCtx }) }
    });
});