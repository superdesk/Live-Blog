'use strict';

define([
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'plugins/wrappup-toggle',
//	'plugins/scroll-pagination',
	'plugins/permanent-link',
	'plugins/user-comments',
	'css!theme/liveblog'
], function() {
	return {
		plugins: [ 'scroll', 'pagination' ]
	};
});
