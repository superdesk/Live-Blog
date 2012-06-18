/*!
 * @author Mihai Balaceanu <mihai.balaceanu@sourcefabric.org>
 * @package 
 * @subpackage 
 * @copyright 2012 Sourcefabric o.p.s.
 * @license http://www.gnu.org/licenses/gpl.txt
 */

define(['jquery'], function($)
{
    return { init: function()
    { 
        $.superdesk.getAction('modules.sandbox').done(function(action)
        {
            action.ScriptPath && require([$.superdesk.apiUrl+action.ScriptPath]);
        });
    }};
});