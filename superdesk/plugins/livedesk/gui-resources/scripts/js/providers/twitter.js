/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/twitter', ['providers','jquery'], function( providers, $ ) {$.extend(providers.twitter, {	init: function() {
		console.log('twitter main init');
	},
});return providers;});