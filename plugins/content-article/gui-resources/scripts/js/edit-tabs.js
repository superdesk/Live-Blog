/*!
 * includes the list of tabs active for edit page
 * these are not plugins
 * 
 * basic tab be an object with 2 keys: 
 *  - control: tab control, the one that activates the tab content box
 *  - content: tab content box - cannot be left empty for now
 *  
 * the 2 objects must be bound together, 
 *  edit view does not handle that automatically
 * 
 * first use case was to add a media tab, 
 *  which has the content box empty in the beginning,
 *  the media plugin binds functionality to it
 */
define
([
    config.guiJs('superdesk/article', 'tabs/media')
], 
function()
{
    return arguments;
});