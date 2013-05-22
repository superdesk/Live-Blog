/*!
 * includes the list of active plugins on the edit page
 * 
 * each plugin must contain a method setArticle( article )
 *  which is called by the edit view to pass the loaded article
 * each plugin must contain a method setParent( editView )
 *  which is called by the edit view to pass itself
 */
define
([
    config.guiJs('superdesk/article', 'plugins/media'),
    config.guiJs('superdesk/article', 'plugins/publishing-control')
], 
function(){ return arguments; });