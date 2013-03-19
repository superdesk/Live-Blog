/*!
 * includes the list of active plugins on the edit page
 * 
 * each plugin must contain a method setArticle( article )
 *  which is called by the edit view to pass the loaded article
 */
define
([
    config.guiJs('superdesk/article', 'plugins/media'),
], 
function(){ return arguments; });